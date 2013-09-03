from __future__ import unicode_literals
import collections
import generator
import twisted.internet.defer
import ipaddr

class _AddressRepository(object):
    """
    queue for storing addresses

    DEPRECATED - delete it
    """

    instance = None
    addresses = None

    def __init__(self):
        self.addresses = collections.deque()

    @classmethod
    def getInstance(cls):
        if cls.instance is None:
            cls.instance = cls()
        return cls.instance

    def __len__(self):
        """
        get count of stored addresses
        """
        return len(self.addresses)

    def insertAddress(self, address):
        self.addresses.append(address)

    def getAddress(self):
        return self.addresses.popleft()

class AddressProducer(object):
    """
    service for producing addresses, which are useable
    """

    __addressGenerator = None
    __referenceRepository = None

    def __init__(self, addressGenerator, referenceRepository):
        """
        addressGenerator - IAddressGenerator provider
        referenceRepository - IUseableReference provider
        """
        self.__addressGenerator = addressGenerator
        self.__referenceRepository = referenceRepository

    def getAddress(self):
        """
        get next address to scan

        return deferred with address
        """
        address = self.__addressGenerator.generate()
        d = twisted.internet.defer.Deferred()
        d2 = twisted.internet.defer.maybeDeferred(
            self.__referenceRepository.isUseable,
            address)
        d2.addCallback(
            _AddressPackage(
                d,
                address,
                self.__addressGenerator,
                self.__referenceRepository))
        return d

class _AddressPackage(object):
    """
    package class
    """

    deferred = None
    address = None
    addressGenerator = None
    referenceRepository = None

    def __init__(self, deferred, address, addressGenerator, referenceRepository):
        self.deferred = deferred
        self.address = address
        self.addressGenerator = addressGenerator
        self.referenceRepository = referenceRepository

    def __call__(self, result):
        if not result:
            self.address = self.addressGenerator.generate()
            d = twisted.internet.defer.maybeDeferred(
                self.referenceRepository.isUseable,
                self.address)
            d.addCallback(self)
        else:
            self.deferred.callback(self.address)

class _AddressCallable(object):

    __callable = None
    __args = None
    __kwargs = None

    def __init__(self, call, *args, **kwargs):
        self.__callable = call
        self.__args = args
        self.__kwargs = kwargs

    def __call__(self):
        return self.__callable(*self.__args, **self.__kwargs)

class Address(object):
    """
    object representing IP address

    address can either be IPv4 or IPv6

    address can be created from string representation or int number
    you can force creation address of specific version by calling factory
    methods makeV4() or makeV6()
    """

    __address = None

    def __init__(self, address):
        """
        create IP address from string/int
        if address is integer < 2**32, IPv4 will be created
        use factory method to force version
        """
        if isinstance(address, _AddressCallable):
            self.__address = address()
        else:
            self.__address = ipaddr.IPAddress(address)

    @classmethod
    def makeV4(cls, address):
        """
        make IPv4 address
        Raises:
            ValueError
        """
        return cls(_AddressCallable(ipaddr.IPAddress, address, 4))

    @classmethod
    def makeV6(cls, address):
        """
        make IPv4 address
        Raises:
            ValueError
        """
        return cls(_AddressCallable(ipaddr.IPAddress, address, 6))

    @property
    def version(self):
        """
        return version of address as integer value
        """
        return self.__address.version

    def __int__(self):
        """
        return integer representation of address
        """
        return int(self.__address)

    def __hex__(self):
        """
        return hexadecimal representation of address
        """
        return hex(self.__address)

    def __len__(self):
        """
        return length of address in bytes
        for IPv4 address returns 4
        for IPv6 address returns 16
        """
        if self.version == 4:
            return 4
        else:
            return 16

    def __add__(self, other):
        """
        Add two addresses. Add operation is realize by converting address to
        an integer, adding them and returning new address of same varsion

        Raises:
            OverflowError if overflow occurs
            TypeError if other isn't type of Address or int
        """
        return self.__arithmetic(other, 1)

    def __sub__(self, other):
        """
        Subtrack two addresses.

        Raises:
            OverflowError if overflow occurs
            TypeError if other isn't type of Address or int
        """
        return self.__arithmetic(other, -1)

    def __arithmetic(self, other, constant):
        """
        constant: 1 for adding, -1 for subtracking
        """
        if isinstance(other, self.__class__):
            if self.version == other.version:
                num = int(other) * constant
                try:
                    if self.version == 4:
                        return self.__class__.makeV4(int(self) + num)
                    else:
                        return self.__class__.makeV6(int(self) + num)
                except ValueError:
                    raise OverflowError, "values oveflowed"
            else:
                return NotImplemented
        else:
            return NotImplemented

    def __unicode__(self):
        return str(self).decode("utf-8")

    def __str__(self):
        return str(self.__address)

    def __repr__(self):
        return "<%s, version: %d ('%s')>" % \
            (self.__class__.__name__, self.version, str(self))

    def __hash__(self):
        return hash(self.__address)

    def __lt__(self, other):
        return self.__cmp(other, -1)

    def __gt__(self, other):
        return self.__cmp(other, 1)

    def __le__(self, other):
        return self.__cmp(other, -1) or self.__cmp(other, 0)

    def __ge__(self, other):
        return self.__cmp(other, 1) or self.__cmp(other, 0)

    def __eq__(self, other):
        return self.__cmp(other, 0)

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        else:
            return not result

    def __cmp(self, other, compare):
        if isinstance(other, self.__class__):
            if self.version == other.version:
                if compare < 0:
                    return int(self) < int(other)
                elif compare > 0:
                    return int(self) > int(other)
                else:
                    return int(self) == int(other)
            else:
                return NotImplemented
        else:
            return NotImplemented

    @property
    def isLinkLocal(self):
        return self.__address.is_link_local

    @property
    def isLoopback(self):
        return self.__address.is_loopback

    @property
    def isMulticast(self):
        return self.__address.is_multicast

    @property
    def isPrivate(self):
        return self.__address.is_private

    @property
    def isReserved(self):
        return self.__address.is_reserved

    @property
    def isUnspecified(self):
        return self.__address.is_unspecified

    @property
    def maxPrefixLength(self):
        return self.__address.max_prefixlen

    @property
    def packed(self):
        return self.__address.packed
