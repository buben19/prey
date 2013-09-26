from __future__ import unicode_literals
from .. import process
from .. import url
from ..services import ServiceProvider
from .. import error
from ..config import Config
from .. import repository
from .. import data
from .. import shedule
from _visitedurl import _VisitedUrl
from queue import WebCrawlerQueue
from ..http.fetch import PageFetchConfig, PageFetcher
from ..address import Address
import twisted.web.client
import twisted.internet.defer
import twisted.internet.ssl
import parser
import twisted.names.client
import deferredaction



class WebCrawlerSupervisor(process.BaseProcess):
    """
    main class for web crawler process
    """

    # urls in queue wich will be scanned in future
    __urls = None

    # urls which are currently crawling
    __progressUrls = None

    # urls which are comparing with database, if the are useable
    __getUrls = None

    # if True, web crawler will strip all url components and fetch only root
    # url
    __rootUrlOnly = False

    # resolver used to resolve all domain names
    resolver = None

    # respositories
    urlReferenceRepository = None
    hostRepository = None
    wwwPageRepository = None
    urlRepository = None

    # distribute addresses
    addressDistributor = None
    urlDistributor = None

    def __init__(self, rootUrlOnly = False):
        """
        urlRootOnly - if True, get method will strip path, queries and fragments
        and fetch only root url
        """
        self.__urls = WebCrawlerQueue()
        self.__progressUrls = set()
        self.__getUrls = set()
        self.__rootUrlOnly = rootUrlOnly

        # create resolver
        self.resolver = twisted.names.client.createResolver()

        # repositories
        sp = ServiceProvider.getInstance()
        self.urlReferenceRepository = sp.getService(repository.WebCrawlerUrlUseableRepository)
        self.hostRepository = sp.getService(repository.HostRepository)
        self.wwwPageRepository = sp.getService(repository.WWWPageRepository)
        self.urlRepository = sp.getService(repository.UrlRepository)

        # distributing addresses
        self.addressDistributor = sp.getService(data.AddressDistributor)
        self.urlDistributor = sp.getService(data.UrlDistributor)

        # register self for consuming urls
        self.urlDistributor.registerConsumer(self)

        # get non-fetched addresses from the repository and fetch them
        self.wwwPageRepository.getNonFetchedAddresses().addCallback(
            self.__nonFetchedAddresses)

    def __nonFetchedAddresses(self, results):
        """
        add addresses into fetch queue
        """
        for address, port, serviceName in results:
            fetchUrl = url.Url(serviceName + '://' + address + ':' + unicode(port))
            if fetchUrl.hasStandardPort:
                fetchUrl.explicitPort = False
            self.newUrl(fetchUrl, 0)

    def runTask(self):
        d = twisted.internet.defer.Deferred()
        try:
            u, scanLevel = self.__urls.popleft()
        except IndexError as e:
            d.errback(error.TaskError("WebCrawlerSupervisor: pop url failed"))
        else:
            self.newTask(
                WebCrawlerTask(u, scanLevel),
                d)
        return d

    def get(self, url):
        if self.__rootUrlOnly:
            del url.query
            del url.path
            del url.fragment
        self.newUrl(url, 0)

    def getWaitingTaskCount(self):
        return len(self.__urls)

    def newUrl(self, url, scanLevel):
        """
        add new url into local queue

        url can't be already in queue or in progress
        in additional url can't be already associated with any page (useable condition)
        """
        def c(isUseable, u, sl):
            self.__getUrls.remove(u)
            if isUseable:
                self.__urls.append(u, sl)
                ServiceProvider.getInstance().getService(shedule.Sheduler).sheduleNext()
        if not url in self.__urls and \
                not url in self.__progressUrls and \
                not url in self.__getUrls:
            self.__getUrls.add(url)
            self.urlReferenceRepository.isUseable(
                url).addCallback(
                    c,
                    url,
                    scanLevel)

    def urlInProgress(self, url):
        """
        store url as url in progress
        if this url is in local queue, remove it
        """
        if url in self.__urls:
            self.__urls.remove(url)
        self.__progressUrls.add(url)

    def urlFinished(self, url):
        """
        progress url has been finished
        """
        self.__progressUrls.remove(url)

    def getMaxTaskCount(self):
        return 1

    def taskFinished(self, task):
        print "-" * 100
        process.BaseProcess.taskFinished(self, task)

class WebCrawlerTask(process.BaseTask):
    """
    object representig single task
    """

    # id of fetched page
    pageId = None

    # first url passed into constructor
    url = None

    # scan level for this task
    scanLevel = None

    # track all visited url information
    # every redirect creates new frame in this structure
    visitedUrls = None

    # store resolved locations and their addresses
    resolveHistory = None

    # list of additional informations for page
    additionalInfo = None

    def __init__(self, url, scanLevel):
        self.url = url
        self.scanLevel = scanLevel
        self.visitedUrls = []
        self.resolveHistory = {}
        self.additionalInfo = []

    def start(self):
        print "crawling: %s, scan level: %d" % (str(self.url), self.scanLevel)
        self.__createUrlFrame(self.url)
        self.nextIteration()

    def nextIteration(self):
        """
        start processing last url
        """

        # get id for url
        self.newCallback(
            self.supervisor.urlRepository.generateUrlId(),
            deferredaction.DeferredUrlId())

    def pageFetchSuccess(self, page):
        self.lastVisited().pageFetched = True
        self.lastVisited().page = page

        # examine content of page
        self.__processPage(page)

    def pageFetchError(self, reason):
        self.lastVisited().pageFetched = False
        self.lastVisited().pageError = reason

    def lastVisited(self):
        return self.visitedUrls[-1]

    def isUrlVisited(self, url):
        """
        returns True, if url is already stored in visited urls
        """
        for i in self.visitedUrls:
            if i.url == url:
                return True
        return False

    def getUrlId(self, url):
        """
        Get id of given url. Raise ValueError if url isn't in visited urls
        """
        for i in self.visitedUrls:
            if i.url == url:
                return i.urlId
        raise ValueError, "url not found"

    def __createUrlFrame(self, url):
        """
        create new url frame

        for successful creation some values can't be None
        ValueError is raised if this condition isn't met
        """

        # mark url as in progress
        self.supervisor.urlInProgress(url)

        if len(self.visitedUrls) > 0:
            if  self.lastVisited().urlId is None or \
                    self.lastVisited().fetchAddress is None or \
                    self.lastVisited().pageFetched is None or \
                    (self.lastVisited().page is not None and \
                    self.lastVisited().pageError is not None):

                # every time, when new frame is created, some fields inf
                # visitedUrls can't be None
                # must be set - debug purpose only
                raise ValueError, "incomplete current visited url structure"
        self.visitedUrls.append(_VisitedUrl(url))

    def gotUrlId(self, urlId):
        """
        store id for current url

        if current url isn't firs, id will be stored as redirect url id for
        previous one
        """
        self.lastVisited().urlId = urlId

        # save redirect url id
        if len(self.visitedUrls) > 1:
            self.visitedUrls[-2].redirectUrlId = urlId

    def doFetch(self):
        """
        fetch last url
        """
        print "fetching:", unicode(self.lastVisited().url), "address:", self.lastVisited().fetchAddress
        fetchConfig = PageFetchConfig(
            self.lastVisited().url)
        fetcher = PageFetcher(
            fetchConfig,
            self.lastVisited().fetchAddress,
            self.lastVisited().url.port)

        # registed callbacks
        self.newCallbacks(
            fetcher.getPage(),
            deferredaction.DeferredPageSuccess(),
            deferredaction.DeferredPageError())

    def __processPage(self, page):
        if page.decodedContent is not None:
            p = parser.WebCrawlerParser()
            print "feeding...", type(page.decodedContent)
            p.feed(page.decodedContent)
            self.lastVisited().pageTitle = p.getTitle()

            # process hrefs
            print "starting processing hrefs"
            urls = set()
            for i in p.getHrefs():
                try:
                    u = url.Url.join(self.lastVisited().url, i)
                except ValueError:
                    continue
                if not u.scheme.lower() in ["http", "https"]:
                    continue
                u.fragment.clear()
                urls.add(u)
            print "hrefs processed"
            for u in urls:
                if u.netloc == self.lastVisited().url.netloc:

                    if self.scanLevel < Config.webCrawlerScanLevel:
                        self.supervisor.newUrl(u, self.scanLevel + 1)
                else:
                    self.supervisor.urlDistributor.distribute(u)

    def saveUrls(self):
        """
        save all visited urls in reverse order
        """
        def c3(result, deferred, updateUrlId):
            self.supervisor.urlRepository.updateRedirectUrlId(
                self.visitedUrls[-1].urlId,
                updateUrlId).addCallback(c2, deferred)
        def c2(result, deferred):
            print "url save complete"
            deferred.callback(result)
        def c(result, deferred, index, updateUrlId):
            redirectUrlId = self.visitedUrls[index].redirectUrlId

            # true at first iteration
            if not index < len(self.visitedUrls) - 1:
                if self.__isUrlIdInVisitedUrls(redirectUrlId):
                    updateUrlId = redirectUrlId
                    redirectUrlId = None

            print "saving url: %s - id: %d - redirect id: %s" % (str(self.visitedUrls[index].url), self.visitedUrls[index].urlId, str(redirectUrlId))
            d2 = self.supervisor.urlRepository.saveUrl(
                self.visitedUrls[index].urlId,
                self.visitedUrls[index].url,
                redirectUrlId)
            if index > 0:
                d2.addCallback(c, deferred, index - 1, updateUrlId)
            else:
                if updateUrlId is None:

                    # not saving urls with infinite loop
                    d2.addCallback(c2, deferred)
                else:

                    # saving inifinite redirect loop, first saved url needs
                    # to be updated with proper redirect urlId
                    d2.addCallback(c3, deferred, updateUrlId)
        d = twisted.internet.defer.Deferred()
        c(None, d, len(self.visitedUrls) - 1, None)
        return d

    def __isUrlIdInVisitedUrls(self, urlId):
        """
        returns true if url ID is in visited urls
        """
        for i in self.visitedUrls:
            if i.urlId == urlId:
                return True
        return False

    def associateUrlsAndHosts(self):
        """
        associate all visited urls and their host id
        """
        d = twisted.internet.defer.Deferred()
        def c(result, deferred):
            print "association complete"
            deferred.callback(None)
        deferreds = []
        for i in self.visitedUrls:
            urlId = i.urlId
            for hostId in i.hostIds:
                print "associating url ID: %d with host ID: %d" % (urlId, hostId)
                deferreds.append(
                    self.supervisor.urlRepository.associateUrlWithHost(
                        urlId, hostId))
        if len(deferreds) > 0:
            dl = twisted.internet.defer.DeferredList(deferreds)
            dl.addCallback(c, d)
        else:
            print "no url-host association happend"
            d.callback(None)
        return d

    def savePageFetchInfo(self):
        """
        associate urls and page, fill getch info
        urls and page must be already saved
        """
        d = twisted.internet.defer.Deferred()
        def c(result, deferred):
            print "save page fetch info completed"
            deferred.callback(None)
        deferreds = []
        for i in self.visitedUrls:
            if i.pageFetched:
                print "saving page fetch info - page ID: %d, URL ID: %d, %s %s %s" % (self.pageId, i.urlId, i.page.version, i.page.status, i.page.message)
                deferreds.append(
                    self.supervisor.wwwPageRepository.savePageAndUrlFetchInfo(
                        self.pageId,
                        i.urlId,
                        i.page.version,
                        i.page.status,
                        i.page.message))
            else:
                print "saving page error extras - page ID: %d, URL ID: %d, message: %s" % (self.pageId, i.urlId, i.pageError)
                deferreds.append(
                    self.supervisor.wwwPageRepository.savePageAndUrlErrorExtras(
                        self.pageId,
                        i.urlId,
                        i.pageError))
        dl = twisted.internet.defer.DeferredList(deferreds).addCallback(c, d)
        return d

    def savePageAdditionalInfo(self):
        d = twisted.internet.defer.Deferred()
        def c(result, deferred):
            deferred.callback(None)
        deferreds = []
        for infoClass, message in self.additionalInfo:
            deferreds.append(
                self.supervisor.wwwPageRepository.saveAdditionalInfo(
                    self.pageId,
                    infoClass,
                    message))
        if len(deferreds) > 0:
            twisted.internet.defer.DeferredList(deferreds).addCallback(c, d)
        else:
            d.callback(None)
        return d

    def processNextUrl(self, url):
        self.__createUrlFrame(url)
        self.nextIteration()

    def setAdditionalInfo(self, infoClass, message):
        self.additionalInfo.append((infoClass, message))

    def allUrlsFinished(self):
        """
        finish all visited urls in supervisor
        """
        for i in self.visitedUrls:
            self.supervisor.urlFinished(i.url)
