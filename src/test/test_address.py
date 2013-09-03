from src.address import Address
import unittest

class TestAddress(object):

    addressVersion = None
    addressLength = None
    addressStr = None
    addressInt = None
    addressLinkLocalStr = None
    addressLoopbackStr = None
    addressMulticastStr = None
    addressPrivateStr = None
    addressReservedStr = None
    addressUnspecifiedStr = None
    address = None

    def _addressInit(self, address):
        self.assertEquals(address.version, self.addressVersion)
        self.assertEquals(str(address), self.addressStr)
        self.assertEquals(int(address), self.addressInt)

    def test_initAddressStr(self):
        self._addressInit(Address(self.addressStr))

    def test_initAddressIntDecimal(self):
        self._addressInit(Address(self.addressInt))

    def test_factoryMethodAddress(self):
        self.assertTrue(False, msg = "overwrite in subclass")

    def test_factoryMethodInt(self):
        self.assertTrue(False, msg = "overwrite in subclass")

    def test_factoryMethodAddressError(self):
        self.assertTrue(False, msg = "overwrite in subclass")

    def test_factoryMethodIntError(self):
        self.assertTrue(False, msg = "overwrite in subclass")

    def test_version(self):
        self.assertEquals(self.address.version, self.addressVersion)

    def test_int(self):
        self.assertEquals(int(self.address), self.addressInt)

    def test_hex(self):
        self.assertEquals(hex(self.address), hex(self.addressInt))

    def test_len(self):
        self.assertEquals(len(self.address), self.addressLength)

    def test_addAddress(self):
        self.address = self.address + Address(self.addressStr)
        self.assertEquals(int(self.address), self.addressInt * 2)

    def test_addNotAddressError(self):
        self.assertEquals(NotImplemented, self.address.__add__(1))
        self.assertEquals(NotImplemented, self.address.__add__(object()))

    def test_addNotSameVersionError(self):
        self.assertTrue(False, msg = "overwrite in subclass")

    def test_addOverflowError(self):
        self.assertRaises(
            OverflowError,
            self.address.__add__,
            Address((2 ** (len(self.address) * 8)) - 1))

    def test_subAddress(self):
        self.address = self.address - Address(self.addressStr)
        self.assertEquals(0, int(self.address))

    def test_subNotAddressError(self):
        self.assertEquals(NotImplemented, self.address.__sub__(1))
        self.assertEquals(NotImplemented, self.address.__sub__(object()))

    def test_subNotSameVersionError(self):
        self.assertTrue(False, msg = "overwrite in subclass")

    def test_subOverflowError(self):
        self.assertRaises(
            OverflowError,
            self.address.__sub__,
            Address((2 ** (len(self.address) * 8)) - 1))

    def test_str(self):
        self.assertEquals(str(self.address), self.addressStr)

    def test_repr(self):
        self.assertEquals(
            repr(self.address),
            "<%s, version: %d ('%s')>" % \
                (self.address.__class__.__name__, self.address.version, str(self.address)))

    def test_hash(self):
        self.assertEquals(hash(self.address), hash(hex(long(self.addressInt))))

    def test_lt(self):
        self.assertTrue(
            self.address < Address(int(self.address) + 1))

    def test_gt(self):
        self.assertTrue(
            self.address > Address(int(self.address) - 1))

    def test_le(self):
        self.assertTrue(
            self.address <= Address(int(self.address) + 1))
        self.assertTrue(
            self.address <= Address(int(self.address)))

    def test_ge(self):
        self.assertTrue(
            self.address >= Address(int(self.address) - 1))
        self.assertTrue(
            self.address >= Address(int(self.address)))

    def test_ltNotAddressError(self):
        self.assertEquals(
            NotImplemented,
            self.address.__lt__(1))
        self.assertEquals(
            NotImplemented,
            self.address.__lt__(object()))

    def test_gtNotAddressError(self):
        self.assertEquals(
            NotImplemented,
            self.address.__gt__(1))
        self.assertEquals(
            NotImplemented,
            self.address.__gt__(object()))

    def test_leNotAddressError(self):
        self.assertEquals(
            NotImplemented,
            self.address.__le__(1))
        self.assertEquals(
            NotImplemented,
            self.address.__le__(object()))

    def test_geNotAddressError(self):
        self.assertEquals(
            NotImplemented,
            self.address.__ge__(1))
        self.assertEquals(
            NotImplemented,
            self.address.__ge__(object()))

    def test_ltNotSameVersionError(self):
        self.assertTrue(False, msg = "overwrite in subclass")

    def test_gtNotSameVersionError(self):
        self.assertTrue(False, msg = "overwrite in subclass")

    def test_leNotSameVersionError(self):
        self.assertTrue(False, msg = "overwrite in subclass")

    def test_geNotSameVersionError(self):
        self.assertTrue(False, msg = "overwrite in subclass")

    def test_eq(self):
        self.assertTrue(
            self.address.__eq__(Address(self.addressStr)))
        self.assertFalse(
            self.address.__eq__(Address(self.addressInt + 1)))

    def test_eqNotAddressError(self):
        self.assertEquals(
            NotImplemented, self.address.__eq__(1))
        self.assertEquals(
            NotImplemented, self.address.__eq__(object()))

    def test_eqNotSameVersionError(self):
        self.assertTrue(False, msg = "overwrite in subclass")

    def test_ne(self):
        self.assertFalse(
            self.address.__ne__(Address(self.addressStr)))
        self.assertTrue(
            self.address.__ne__(Address(self.addressInt + 1)))

    def test_neNotAddressError(self):
        self.assertEquals(
            NotImplemented, self.address.__ne__(1))
        self.assertEquals(
            NotImplemented, self.address.__ne__(object()))

    def test_neNotSameVersionError(self):
        self.assertTrue(False, msg = "overwrite in subclass")

    def test_isLinkLocalFalse(self):
        self.assertFalse(self.address.isLinkLocal)

    def test_isLoopbackFalse(self):
        self.assertFalse(self.address.isLoopback)

    def test_isMulticastFalse(self):
        self.assertFalse(self.address.isMulticast)

    def test_isPrivateFalse(self):
        self.assertFalse(self.address.isPrivate)

    def test_isReservedFalse(self):
        self.assertFalse(self.address.isReserved)

    def test_isUnspecifiedFalse(self):
        self.assertFalse(self.address.isUnspecified)

    def test_isLinkLocalTrue(self):
        self.assertTrue(
            Address(self.addressLinkLocalStr).isLinkLocal)

    def test_isLoopbackTrue(self):
        self.assertTrue(
            Address(self.addressLoopbackStr).isLoopback)

    def test_isMulticastTrue(self):
        self.assertTrue(
            Address(self.addressMulticastStr).isMulticast)

    def test_isPrivateTrue(self):
        self.assertTrue(
            Address(self.addressPrivateStr).isPrivate)

    def test_isReservedTrue(self):
        self.assertTrue(
            Address(self.addressReservedStr).isReserved)

    def test_isUnspecifiedTrue(self):
        self.assertTrue(
            Address(self.addressUnspecifiedStr).isUnspecified)

class TestIPv4Address(unittest.TestCase, TestAddress):

    ipv6AddressStr = None
    ipv6AddressInt = None

    def setUp(self):
        self.addressVersion = 4
        self.addressLength = 4
        self.addressStr = '100.110.120.130'
        self.addressInt = 1684961410
        self.addressLinkLocalStr = "169.254.0.1"
        self.addressLoopbackStr = "127.0.0.1"
        self.addressMulticastStr = "224.0.0.1"
        self.addressPrivateStr = "192.168.0.1"
        self.addressReservedStr = "240.0.0.1"
        self.addressUnspecifiedStr = "0.0.0.0"
        self.address = Address(self.addressStr)
        self.ipv6AddressStr = "fe80:0000:0000:0000:021b:77ff:fbd6:7860"
        self.ipv6AddressInt = 338288524927261089654170743795120240736L

    def test_factoryMethodAddress(self):
        self._addressInit(Address.makeV4(self.addressStr))

    def test_factoryMethodInt(self):
        self._addressInit(Address.makeV4(self.addressStr))

    def test_factoryMethodAddressError(self):
        self.assertRaises(ValueError, Address.makeV4, self.ipv6AddressStr)

    def test_factoryMethodIntError(self):
        self.assertRaises(ValueError, Address.makeV4, self.ipv6AddressInt)

    def test_addNotSameVersionError(self):
        self.assertEquals(
            NotImplemented,
            self.address.__add__(Address(self.ipv6AddressStr)))

    def test_subNotSameVersionError(self):
        self.assertEquals(
            NotImplemented,
            self.address.__sub__(Address(self.ipv6AddressStr)))

    def test_ltNotSameVersionError(self):
        self.assertEquals(
            NotImplemented,
            self.address.__lt__(Address(self.ipv6AddressStr)))

    def test_gtNotSameVersionError(self):
        self.assertEquals(
            NotImplemented,
            self.address.__gt__(Address(self.ipv6AddressStr)))

    def test_leNotSameVersionError(self):
        self.assertEquals(
            NotImplemented,
            self.address.__le__(Address(self.ipv6AddressStr)))

    def test_geNotSameVersionError(self):
        self.assertEquals(
            NotImplemented,
            self.address.__ge__(Address(self.ipv6AddressStr)))

    def test_eqNotSameVersionError(self):
        self.assertEquals(
            NotImplemented,
            self.address.__eq__(Address(self.ipv6AddressStr)))

    def test_neNotSameVersionError(self):
        self.assertEquals(
            NotImplemented,
            self.address.__ne__(Address(self.ipv6AddressStr)))

class TestIPv6Address(unittest.TestCase, TestAddress):

    ipv4AddressStr = None
    ipv4AddressInt = None

    def setUp(self):
        self.addressVersion = 6
        self.addressLength = 16
        self.addressStr = '2001:db8::1428:57ab'
        self.addressInt = 42540766411282592856903984951992014763L
        self.addressLinkLocalStr = "fe80::1"
        self.addressLoopbackStr = "::1"
        self.addressMulticastStr = "ff00::1"
        self.addressPrivateStr = "fc00::1"
        self.addressReservedStr = "::1"
        self.addressUnspecifiedStr = "::"
        self.address = Address(self.addressStr)
        self.ipv4AddressStr = "100.110.120.130"
        self.ipv4AddressInt = 1684961410

    def test_factoryMethodAddress(self):
        self._addressInit(Address.makeV6(self.addressStr))

    def test_factoryMethodInt(self):
        self._addressInit(Address.makeV6(self.addressStr))

    def test_factoryMethodAddressError(self):
        self.assertRaises(ValueError, Address.makeV6, self.ipv4AddressStr)

    def test_factoryMethodIntError(self):
        self.assertRaises(ValueError, Address.makeV6, self.addressInt ** 8)

    def test_addNotSameVersionError(self):
        self.assertEquals(
            NotImplemented,
            self.address.__add__(Address(self.ipv4AddressStr)))

    def test_subNotSameVersionError(self):
        self.assertEquals(
            NotImplemented,
            self.address.__sub__(Address(self.ipv4AddressStr)))

    def test_ltNotSameVersionError(self):
        self.assertEquals(
            NotImplemented,
            self.address.__lt__(Address(self.ipv4AddressStr)))

    def test_gtNotSameVersionError(self):
        self.assertEquals(
            NotImplemented,
            self.address.__gt__(Address(self.ipv4AddressStr)))

    def test_leNotSameVersionError(self):
        self.assertEquals(
            NotImplemented,
            self.address.__le__(Address(self.ipv4AddressStr)))

    def test_geNotSameVersionError(self):
        self.assertEquals(
            NotImplemented,
            self.address.__ge__(Address(self.ipv4AddressStr)))

    def test_eqNotSameVersionError(self):
        self.assertEquals(
            NotImplemented,
            self.address.__eq__(Address(self.ipv4AddressStr)))

    def test_neNotSameVersionError(self):
        self.assertEquals(
            NotImplemented,
            self.address.__ne__(Address(self.ipv4AddressStr)))

