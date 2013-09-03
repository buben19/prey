"""
data distribution
"""

import zope.interface
import interfaces



class Distributor(object):
    """
    distribute data to multiple producents
    """

    zope.interface.implements(interfaces.IProducer)

    __consumers = None

    def __init__(self):
        self.__consumers = set()

    def registerConsumer(self, consumer):
        """
        registed new consumer
        """
        if consumer in self.__consumers:
            raise KeyError, "consumers is already registered"
        else:
            self.__consumers.add(consumer)

    def unregisterConsumer(self, consumer):
        """
        """
        if not consumer in self.__consumers:
            raise KeyError, "consumer isn't registered"
        else:
            return self.__consumers.remove(consumer)

    def distribute(self, data):
        """
        send object to multiple producents
        """
        for consumer in self.__consumers:
            consumer.get(data)

class AddressDistributor(Distributor):
    """
    distribute addresses
    """

class UrlDistributor(Distributor):
    """
    distribute url
    """
