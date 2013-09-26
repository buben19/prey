from __future__ import unicode_literals
from .. import address
from .. import process
from .. import url
from ..resolve import DNSResolveProcessor, ResolveResults
from ..tools import Counter
from ..http.page import HTTPPage, PageTools, SUCCESS, REDIRECT, NOT_FOUND
import twisted.internet.defer
import twisted.web.error

class DeferredUrlId(process.DeferredAction):

    def __isAddress(self, string):
        try:
            address.Address(string)
            return True
        except Exception:
            return False

    def action(self, urlId):
        self.task.gotUrlId(urlId)
        print "url id:", urlId

        if self.__isAddress(self.task.lastVisited().url.host):

            # location of url is address, no need to resolve
            self.task.lastVisited().fetchAddress = self.task.lastVisited().url.host
            self.task.newCallback(
                self.task.supervisor.hostRepository.getHost(
                    address.Address(self.task.lastVisited().url.host)),
                DeferredGetHost(
                    Counter(1),
                    address.Address(self.task.lastVisited().url.host)))

        else:

            # location of url have to be resolved
            if self.task.lastVisited().url.host in self.task.resolveHistory:

                # location is already resolved, pick up previous results from
                # resolve hostory
                # TODO: implement resolve history
                pass

            else:
                print "resolving location:", self.task.lastVisited().url.host
                # resolve
                resolveResults = ResolveResults()
                self.task.newCallbacks(
                    self.task.supervisor.resolver.lookupAllRecords(
                        self.task.lastVisited().url.host),
                    DeferredResolveSuccess(resolveResults),
                    DeferredResolveError(resolveResults))

class DeferredResolveBase(process.DeferredAction):

    resolveResults = None

    def __init__(self, resolveResults):
        self.resolveResults = resolveResults

    def getHostIds(self):

        if len(self.resolveResults) > 0:

            # some addresses has been resolved
            counter = Counter(len(self.resolveResults))

            #self.task.gotFetchAddress(processor.getIPv4()[0])

            for i in self.resolveResults:
                i = address.Address(i)
                self.task.newCallback(
                    self.task.supervisor.hostRepository.getHost(i),
                    DeferredGetHost(counter, i))
        else:

            # no resolved addresses, error
            print "resolve error"
            self.task.pageFetchError("URL location can't be resolved")
            self.task.newCallback(
                twisted.internet.defer.succeed(None),
                DeferredPageFetchError())

    def action(self, result):
        self.processResolve(result)
        if self.resolveResults.isDone():
            self.getHostIds()


class DeferredResolveSuccess(DeferredResolveBase):

    def processResolve(self, result):

        answers, authority, additional = result

        # process resolve results
        processor = DNSResolveProcessor(answers)

        # debug output
        print "url location resolved"
        print (" " * 4) + "IPv4:"
        for i in processor.getIPv4():
            print (" " * 8) + i
        print (" " * 4) + "IPv6:"
        for i in processor.getIPv6():
            print (" " * 8) + i

        # save resolved addresses
        l = []
        l.extend(processor.getIPv4())
        l.extend(processor.getIPv6())
        self.resolveResults.addAddresses(l)

        if self.task.lastVisited().fetchAddress is None and \
                len(processor.getIPv4()) > 0:
            self.task.lastVisited().fetchAddress = processor.getIPv4()[0]

        # examine cnames
        cnames = processor.getCnames()

        if len(cnames) > 0:
            self.__processCnames(cnames)

    def __processCnames(self, cnames):

        # debug output
        print "got some CNAMEs:"
        for i in cnames:
            print (" " * 4) + i

        # TODO: resolve history
        # got some cnames, resolve them
        self.resolveResults.expectNextAddresses(len(cnames))
        for i in cnames:
            self.task.newCallbacks(
                self.task.supervisor.resolver.lookupAllRecords(i),
                DeferredResolveSuccess(self.resolveResults),
                DeferredResolveError(self.resolveResults))

class DeferredResolveError(DeferredResolveBase):

    def processResolve(self, reason):
        self.resolveResults.noAddresses()

class DeferredGetHost(process.DeferredAction):

    counter = None
    address = None

    def __init__(self, counter, address):
        self.counter = counter
        self.address = address

    def action(self, result):
        if len(result) > 0:
            print "ip address %s has already saved host id: %d" % (self.address, result[0][0])

            # record about host exist
            self.task.lastVisited().hostIds.append(result[0][0])

            self.counter.decrement()
            if self.counter.isZero():
                self.task.doFetch()
        else:
            print "ip address %s isn't in database, generating new host id" % (self.address,)

            # host doesn't exist
            self.task.newCallback(
                self.task.supervisor.hostRepository.generateHostId(),
                DeferredHostGenerateId(
                    self.counter,
                    self.address))

class DeferredHostGenerateId(process.DeferredAction):

    counter = None
    address = None

    def __init__(self, counter, address):
        self.counter = counter
        self.address = address

    def action(self, hostId):
        print "saving non-scanned host %s with id: %d" % (str(self.address), hostId)
        self.task.newCallback(
            self.task.supervisor.hostRepository.saveHost(
                hostId,
                self.address,
                'not-scanned'),         # address isn't scanned yet
            DeferredHostSave(self.counter, self.address, hostId))

class DeferredHostSave(process.DeferredAction):

    counter = None
    address = None
    hostId = None

    def __init__(self, counter, address, hostId):
        self.counter = counter
        self.address = address
        self.hostId = hostId

    def action(self, result):
        self.task.supervisor.addressDistributor.distribute(self.address)
        self.task.lastVisited().hostIds.append(self.hostId)

        self.counter.decrement()
        if self.counter.isZero():
            self.task.doFetch()

class DeferredPageSuccess(process.DeferredAction):

    def pageSuccess(self, page):
        self.task.newCallback(
            twisted.internet.defer.succeed(None),
            DeferredPageFetchSuccess())

    def pageRedirect(self, page):
        location = PageTools.getLocation(page.headers)
        if location is not None:
            self.redirectWithLocation(page, location)
        else:
            self.redirectWithNoLocation(page)

    def redirectWithLocation(self, page, location):
        if self.task.isUrlVisited(location):
            self.urlVisited(location)
        else:
            self.urlNotVisited(location)

    def urlVisited(self, location):
        print "infinite redirection"

        # url is visited in this task - infinite redirection
        # get urlId of location and store it in lastVisited structure
        self.task.lastVisited().redirectUrlId = self.task.getUrlId(location)
        self.task.setAdditionalInfo("error", "inifinite redirection loop")
        self.task.newCallback(
            twisted.internet.defer.succeed(None),
            DeferredPageFetchError())

    def urlNotVisited(self, location):

        # not visited
        # look into database, if new url were fetched in the past
        self.task.newCallback(
            self.task.supervisor.wwwPageRepository.isPageFetched(location),
            DeferredIsPageFetchedTest(
                location))

    def redirectWithNoLocation(self, page):
        self.task.setAdditionalInfo("error", "got redirect with no location")
        self.task.newCallback(
            twisted.internet.defer.succeed(None),
            DeferredPageFetchError())

    def pageNotFound(self, page):
        self.task.newCallback(
            twisted.internet.defer.succeed(None),
            DeferredPageFetchSuccess())

    def action(self, page):
        self.task.pageFetchSuccess(page)

        if page.pageInfo == SUCCESS:
            self.pageSuccess(page)
        elif page.pageInfo == REDIRECT:
            self.pageRedirect(page)
        else:
            self.pageNotFound(page)


class DeferredPageError(process.DeferredAction):

    def action(self, reason):
        # no response from server for any reason
        self.task.pageFetchError(reason.getErrorMessage())
        self.task.newCallback(
            twisted.internet.defer.succeed(None),
            DeferredPageFetchError())

class DeferredIsPageFetchedTest(process.DeferredAction):

    url = None

    def __init__(self, url):
        self.url = url

    def action(self, result):

        if result:

            # url is already fetched
            print "url %s is already fetched" % str(self.url)
            self.task.newCallback(
                twisted.internet.defer.succeed(None),
                DeferredPageAlreadyFetched(self.url))

        else:

            # not fetched, process it
            self.task.processNextUrl(self.url)

class DeferredPageFetchBase(process.DeferredAction):
    """
    base class for final stage of webcrawler
    """

    waitDeferred = None

    def __call__(self, result, *args, **kwargs):
        self.waitDeferred = twisted.internet.defer.Deferred()
        self.task.newCallback(
            self.waitDeferred,
            DeferredWaitAction())
        print "wait deferred created"
        return process.DeferredAction.__call__(self, result, *args, **kwargs)

    def done(self, result):
        """
        call this when everything is done
        """
        self.waitDeferred.callback(None)

class DeferredPageFetchSuccess(DeferredPageFetchBase):
    """
    """

    def action(self, result):
        self.task.supervisor.wwwPageRepository.generatePageId().addCallback(
                self.__generatePageId)

    def __generatePageId(self, pageId):
        self.task.pageId = pageId
        print "generated page ID:", pageId

        self.task.saveUrls().addCallback(
            self.__saveUrls)

    def __saveUrls(self, result):
        self.task.associateUrlsAndHosts().addCallback(
            self.__associateUrls)

    def __associateUrls(self, result):
        print "saving page - id:", self.task.pageId
        print (" " * 4) + "page headers:"
        for header in self.task.lastVisited().page.headers:
            print (" " * 8) + header.name, "-", header.value
        self.task.supervisor.wwwPageRepository.savePage(
            self.task.pageId,
            self.task.lastVisited().page.headers,
            self.task.lastVisited().pageTitle).addCallback(
                self.__savePage)

    def __savePage(self, result):
        self.task.savePageAdditionalInfo().addCallback(
            self.__savePageAdditionalInfo)

    def __savePageAdditionalInfo(self, result):
        self.task.savePageFetchInfo().addCallback(
            self.done)

class DeferredPageFetchError(DeferredPageFetchBase):

    def action(self, result):
        self.task.supervisor.wwwPageRepository.generatePageId().addCallback(
                self.__generatePageId)

    def __generatePageId(self, pageId):
        self.task.pageId = pageId
        print "generated page ID:", pageId

        self.task.saveUrls().addCallback(
            self.__saveUrls)

    def __saveUrls(self, result):
        self.task.associateUrlsAndHosts().addCallback(
            self.__associateUrls)

    def __associateUrls(self, result):
        print "saving page - id:", self.task.pageId
        self.task.supervisor.wwwPageRepository.savePage(
            self.task.pageId,
            [],
            None).addCallback(
                self.__savePage)

    def __savePage(self, result):
        self.task.savePageAdditionalInfo().addCallback(
            self.__savePageAdditionalInfo)

    def __savePageAdditionalInfo(self, result):
        self.task.savePageFetchInfo().addCallback(
            self.done)

class DeferredPageAlreadyFetched(DeferredPageFetchBase):

    url = None

    def __init__(self, url):
        self.url = url

    def action(self, result):
        self.task.supervisor.wwwPageRepository.getPageId(
            self.url).addCallback(self.__getPageId)

    def __getPageId(self, pageId):
        self.task.pageId = pageId
        self.task.supervisor.urlRepository.getUrl(
            self.url).addCallback(
                self.__getRedirectUrlId)

    def __getRedirectUrlId(self, result):
        self.task.lastVisited().redirectUrlId = result[0][0]
        self.task.saveUrls().addCallback(
            self.__saveUrls)

    def __saveUrls(self, result):
        self.task.associateUrlsAndHosts().addCallback(
            self.__associateUrls)

    def __associateUrls(self, result):
        self.task.savePageFetchInfo().addCallback(
            self.done)

class DeferredWaitAction(process.DeferredAction):
     def action(self, result):
         self.task.allUrlsFinished()
