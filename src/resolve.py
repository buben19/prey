from __future__ import unicode_literals
import StringIO
import socket
from tools import Counter

class DNSResolveProcessor(object):

    __ipv4 = None
    __ipv6 = None
    __cnames = None

    def __init__(self, headerList):
        self.__ipv4 = []
        self.__ipv6 = []
        self.__cnames = []
        self.__processResolve(headerList)

    def __processResolve(self, headerList):

        # iterate over list of RRHeader instances with answers
        for i in headerList:

            # create file-like string object
            f = StringIO.StringIO()
            if i.type == 0x01:

                # process A record
                i.payload.encode(f)
                self.ipv4(socket.inet_ntop(socket.AF_INET, f.getvalue()))

            elif i.type == 0x1c:

                # process AAAA record
                i.payload.encode(f)
                self.ipv6(socket.inet_ntop(socket.AF_INET6, f.getvalue()))

            elif i.type == 0x05:

                # process CNAME
                self.cname(str(i.payload.name))

    def ipv4(self, address):
        self.__ipv4.append(address)

    def ipv6(self, address):
        self.__ipv6.append(address)

    def cname(self, cname):
        self.__cnames.append(cname)

    def getIPv4(self):
        return self.__ipv4

    def getIPv6(self):
        return self.__ipv6

    def getCnames(self):
        return self.__cnames

class ResolveResults(object):
    """
    store resolve results
    """

    __counter = None
    __addresses = None

    def __init__(self):
        self.__counter = Counter(1)
        self.__addresses = set()

    def addAddresses(self, addresses):
        self.__addresses.update(addresses)
        self.__counter.decrement()

    def noAddresses(self):
        """
        expected addresses aren't availible
        """
        self.__counter.decrement()

    def expectNextAddresses(self, count = 1):
        """
        call this, when additional addresses are expected
        """
        self.__counter.add(count)

    def isDone(self):
        """
        returns True if all expected addresses has been added
        """
        return self.__counter.isZero()

    def __len__(self):
        return len(self.__addresses)

    def __iter__(self):
        return self.__addresses.__iter__()
