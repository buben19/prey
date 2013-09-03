from __future__ import unicode_literals
import collections

class WebCrawlerQueue(object):

    __urls = None
    __scanLevels = None

    def __init__(self):
        self.__urls = collections.deque()
        self.__scanLevels = collections.deque()

    def __len__(self):
        return len(self.__urls)

    def append(self, url, scanLevel):
        self.__urls.append(url)
        self.__scanLevels.append(scanLevel)

    def popleft(self):
        u = self.__urls.popleft()
        scanLevel = self.__scanLevels.popleft()
        return (u, scanLevel)

    def __contains__(self, url):
        return url in self.__urls

    def remove(self, url):
        """
        remove url from queue
        """
        for i in xrange(len(self.__urls)):
            if self.__urls[i] == url:
                del self.__urls[i]
                del self.__scanLevels[i]
                break

