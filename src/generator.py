"""
generate adresses
"""


import random
import time
import os
import zope.interface
import interfaces
import ipaddr
import address

class RandomIPV4AddressGenerator(object):
    """
    generate addresses
    """

    zope.interface.implements(interfaces.IIPv4AddressGenerator)

    def __init__(self):
        random.seed(int(time.time()) ^ os.getgid())

    def generate(self):
        """
        return IPV4 address as string
        """
        tmp = []
        for i in xrange(4):
            tmp.append(str(random.randint(0, 255)))
        return address.Address(".".join(tmp))

class PublicIPV4AddressGenerator():
    """
    generate public IPv4 address
    """

    zope.interface.implements(interfaces.IIPv4AddressGenerator)

    generator = None

    def __init__(self, generator):
        if not interfaces.IIPv4AddressGenerator.providedBy(generator):
            raise AttributeError, "generator is not IIPv4AddressGenerator provider"
        else:
            self.generator = generator

    def generate(self):
        while True:
            address = self.generator.generate()
            if not address.isLinkLocal and \
                    not address.isLoopback and \
                    not address.isMulticast and \
                    not address.isPrivate and \
                    not address.isReserved and \
                    not address.isUnspecified:
                return address
