from __future__ import unicode_literals
import HTMLParser

class WebCrawlerParser(HTMLParser.HTMLParser):

    __hrefs = None
    __titleOpen = None
    __title = None

    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)
        self.__hrefs = []
        self.__titleOpen = False

    def handle_starttag(self, tag, attrs):
        if tag.lower() == 'a':
            for attrib in attrs:
                if attrib[0].lower() == 'href':
                    self.__hrefs.append(attrib[1])
        if tag.lower() == 'title' and self.__title is None:
            self.__titleOpen = True

    def handle_data(self, data):
        if self.__titleOpen:
            self.__titleOpen = False
            self.__title = data

    def getHrefs(self):
        return self.__hrefs

    def getTitle(self):
        return self.__title
