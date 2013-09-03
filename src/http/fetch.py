from __future__ import unicode_literals
from ..url import Url
from page import HTTPPage, _TwistedHTTPClientContainer
from twisted.internet.defer import Deferred
from twisted.internet.ssl import ClientContextFactory
from twisted.web.client import HTTPClientFactory, HTTPPageGetter
import twisted.internet.reactor
from headers import Header
from cookies import Cookie
import collections



class PageFetchConfig(object):
    """
    specify attributes for fetcher
    """

    __url = None
    __method = None
    __postData = None
    __headers = None
    __agent = None
    __timeout = None
    __cookies = None

    def __init__(self, url, method = "GET", postData = None, headers = [],
            agent = None, timeout = 0, cookies = []):
        self.__url = self.__getUrl(url)
        self.__method = method
        self.__postData = postData
        self.__headers = self.__getHeadersList(headers)
        self.__agent = agent
        self.__timeout = timeout
        self.__cookies = self.__getCookiesList(cookies)

    @property
    def url(self):
        return self.__url

    @property
    def method(self):
        return self.__method

    @property
    def postData(self):
        return self.__postData

    @property
    def headers(self):
        return self.__headers

    @property
    def agent(self):
        return self.__agent

    @property
    def timeout(self):
        return self.__timeout

    @property
    def cookies(self):
        return self.__cookies

    def __getHeader(self, header):
        if isinstance(header, Header):
            return header
        raise TypeError, "value must be instance of Header"

    def __getHeadersList(self, headers):
        l = []
        for header in headers:
            l.append(self.__getHeader(header))
        return l

    def __getCookie(self, cookie):
        if isinstance(cookie, Cookie):
            return cookie
        elif isinstance(cookie, basestring):
            return Cookie.fromString(cookie)
        else:
            raise TypeError, "cookie must be instance of Cookie or string"

    def __getUrl(self, url):
        if isinstance(url, Url):
            return url
        else:
            return Url(url)

    def __getCookiesList(self, cookies):
        l = []
        for cookie in cookies:
            l.append(self.__getCookie(cookie))
        return l

class PageFetcher(object):

    __fetchConfig = None
    __fetchAddress = None
    __fetchPort = None
    __reactor = None

    def __init__(self, fetchConfig, fetchAddress, fetchPort, reactor = None):
        if not isinstance(fetchConfig, PageFetchConfig):
            raise TypeError, "wrong config"
        self.__fetchConfig = fetchConfig
        self.__fetchAddress = fetchAddress
        self.__fetchPort = fetchPort
        if not reactor:
            self.__reactor = twisted.internet.reactor
        else:
            self.__reactor = reactor

    @property
    def config(self):
        return self.__fetchConfig

    def getPage(self):
        """
        return deferred with page
        """
        # TODO: convert content of headers and cookies to bytes
        d = Deferred()
        factory = _PageFetcherFactory(
            str(self.__fetchConfig.url),
            method          = self.__bytesOrNone(self.__fetchConfig.method),
            postdata        = self.__bytesOrNone(self.__fetchConfig.postData),
            headers         = self.__headersDict(self.__fetchConfig.headers),
            agent           = self.__userAgent(self.__fetchConfig.agent),
            timeout         = self.__fetchConfig.timeout,
            cookies         = self.__cookiesDict(self.__fetchConfig.cookies),
            followRedirect  = False)
        factory.deferred.addBoth(
            self.__pageFetched,
            factory,
            d)
        if self.__fetchConfig.url.scheme == "https":
            self.__fetchHttps(factory)
        else:
            self.__fetchHttp(factory)
        return d

    def __bytesOrNone(self, value):
        if value is None:
            return value
        elif isinstance(value, unicode):
            return value.encode("utf-8")
        elif isinstance(value, str):
            return value
        else:
            return str(value)

    def __pageFetched(self, pageResult, factory, deferred):
        if isinstance(pageResult, basestring) or \
                isinstance(pageResult.value, twisted.web.error.Error):

            # communication with server happend
            deferred.callback(
                HTTPPage(
                    _TwistedHTTPClientContainer(factory, pageResult)))
        else:

            # error for any other reason (e.g. timeout)
            deferred.errback(pageResult)

    def __fetchHttp(self, factory):
        self.__reactor.connectTCP(
            str(self.__fetchAddress),
            self.__fetchPort,
            factory)

    def __fetchHttps(self, factory):
        self.__reactor.connectSSL(
            str(self.__fetchAddress),
            self.__fetchPort,
            factory,
            ClientContextFactory())

    def __cookiesDict(self, cookies):
        d = collections.OrderedDict()
        for cookie in cookies:
            d[cookie.name.encode("utf-8")] = cookie.value.encode("utf-8")
        return d

    def __userAgent(self, agent):
        if agent is not None:
            return self.__bytesOrNone(agent)
        else:
            return b""

    def __headersDict(self, headers):
        d = {}
        for header in headers:
            d[header.name.encode("utf-8")] = header.value.encode("utf-8")
        return d

class _PageFetcherFactory(HTTPClientFactory):

    def __init__(self, *args, **kwargs):
        HTTPClientFactory.__init__(self, *args, **kwargs)
        self.protocol = _PageFetcherProtocol
        self.orderedHeaders = []

class _PageFetcherProtocol(HTTPPageGetter):

    def handleHeader(self, key, value):
        """
        hook method and save headers in their right order
        """
        HTTPPageGetter.handleHeader(self, key, value)
        self.factory.orderedHeaders.append(Header(key.decode("utf-8"), value.decode("utf-8")))
