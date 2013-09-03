from __future__ import unicode_literals

class _VisitedUrl(object):

    __url = None
    __urlId = None
    __redirectUrlId = None
    __fetchAddress = None
    __hostIds = None

    # true if page has been succesfully fetched, False otherwire
    __pageFetched = None

    # page received from the server
    __page = None

    # reason for unsuccesful page fetch
    __pageError = None

    # page title parsed from the page
    __pageTitle = None

    def __init__(self, url):
        self.__url = url
        self.__hostIds = []

    @property
    def url(self):
        return self.__url

    @property
    def urlId(self):
        return self.__urlId

    @urlId.setter
    def urlId(self, urlId):
        self.__setProperty('urlId', urlId)

    @property
    def redirectUrlId(self):
        return self.__redirectUrlId

    @redirectUrlId.setter
    def redirectUrlId(self, redirectUrlId):
        self.__setProperty('redirectUrlId', redirectUrlId)

    @property
    def fetchAddress(self):
        return self.__fetchAddress

    @fetchAddress.setter
    def fetchAddress(self, fetchAddress):
        self.__setProperty('fetchAddress', fetchAddress)

    @property
    def hostIds(self):
        return self.__hostIds

    @property
    def pageFetched(self):
        return self.__pageFetched

    @pageFetched.setter
    def pageFetched(self, pageFetched):
        self.__setProperty('pageFetched', pageFetched)

    @property
    def page(self):
        return self.__page

    @page.setter
    def page(self, page):
        self.__setProperty('page', page)

    @property
    def pageError(self):
        return self.__pageError

    @pageError.setter
    def pageError(self, pageError):
        self.__setProperty('pageError', pageError)

    @property
    def pageTitle(self):
        return self.__pageTitle

    @pageTitle.setter
    def pageTitle(self, pageTitle):
        self.__setProperty('pageTitle', pageTitle)

    def __setProperty(self, name, value):
        if getattr(self, name) is None:
            setattr(self, self.__class__.__name__ + "__" + name, value)
        else:
            raise ValueError, "%s isn't None" % (name,)
