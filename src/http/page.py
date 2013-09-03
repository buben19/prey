from __future__ import unicode_literals
import twisted.web.error
import twisted.python.failure
import re
from ..python.orderedmultidict1d import omdict1D
from ..url import Url


class HTTPPage(object):
    """
    representation of html page
    """

    __pageContainer = None
    __decodedContent = None

    def __init__(self, container):
        if not isinstance(container, _BasePageContainer):
            raise TypeError, "not page container"
        self.__pageContainer = container

    @property
    def pageInfo(self):
        """
        information about fetching page (e.g. Success, Redirect,
        RedirectWithNoLocation)
        """
        return self.__pageContainer.pageInfo

    @property
    def version(self):
        return self.__pageContainer.version

    @property
    def status(self):
        return self.__pageContainer.status

    @property
    def message(self):
        return self.__pageContainer.message

    @property
    def headers(self):
        return self.__pageContainer.headers

    @property
    def byteContent(self):
        """
        return content as bytes
        """
        return self.__pageContainer.byteContent

    @property
    def decodedContent(self):
        """
        decode content into utf-8 by server referenced charset
        """
        if self.__decodedContent is None and self.byteContent is not None:
            charset = PageTools.getCharset(self.headers)
            if charset is None:
                charset = "utf-8"
            self.__decodedContent = self.byteContent.decode(charset, "ignore")
        return self.__decodedContent

class PageTools(object):
    """
    utility methods for extracting data from pages
    """

    _charsetPattern = re.compile(r"charset=(?P<charset>[\w-]+)", re.IGNORECASE)

    @classmethod
    def getCharset(cls, headers):
        """
        go throught page headers and try determine used encoding. If encoding
        information isn't in the headers or unsupported encoding is specified,
        return None
        """
        for header in headers:
            if header.name.lower() == "content-type":
                match = cls._charsetPattern.search(header.value)
                if match and match.group('charset'):
                    try:
                        b"".decode(match.group('charset'))
                        return match.group('charset')
                    except LookupError:
                        pass
        return None


    @classmethod
    def getLocation(cls, headers):
        """
        go throught headers and try find header Location. If found, return
        its url as Url object, otherwise return None
        """
        for header in headers:
            if header.name.lower() == "location":
                try:
                    return Url(header.value)
                except ValueError:
                    pass
        return None

    @classmethod
    def getCookies(cls, headers):
        pass

class _BasePageContainer(object):
    """
    adapter class for wrapping pages
    """

class _TwistedHTTPClientContainer(_BasePageContainer):

    __clientFactory = None
    __pageResult = None
    __pageInfo = None

    def __init__(self, clientFactory, pageResult):
        self.__clientFactory = clientFactory
        self.__pageResult = pageResult

        if not isinstance(pageResult, twisted.python.failure.Failure):
            self.__pageInfo = SUCCESS
        elif self.status.startswith("3"):

            # 3xx status codes
            self.__pageInfo = REDIRECT
        else:
            self.__pageInfo = NOT_FOUND


    @property
    def version(self):
        return self.__clientFactory.version.decode("utf-8")

    @property
    def status(self):
        return self.__clientFactory.status.decode("utf-8")

    @property
    def message(self):
        return self.__clientFactory.message.decode("utf-8")

    @property
    def pageInfo(self):
        return self.__pageInfo

    @property
    def headers(self):
        return self.__clientFactory.orderedHeaders

    @property
    def byteContent(self):
        if self.pageInfo is SUCCESS:
            return self.__pageResult
        else:
            return self.__pageResult.value.response

class _PageInfo(object):
    """
    Information about page fetch
    """

# page info constants
SUCCESS                         = _PageInfo()
REDIRECT                        = _PageInfo()
NOT_FOUND                       = _PageInfo()
