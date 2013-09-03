import unittest
from src.services import ServiceProvider, lookupService

class TestServiceProvicer(unittest.TestCase):

    provider = None

    def setUp(self):
        self.provider = ServiceProvider()

    def tearDown(self):
        self.provider = None

    def test_registerService(self):
        self.assertFalse(str in self.provider)
        self.assertEqual(self.provider, self.provider.registerService(str))
        self.assertTrue(str in self.provider)

    def test_registerServiceAlreadyRegisteredError(self):
        self.assertFalse(str in self.provider)
        self.assertEqual(self.provider, self.provider.registerService(str))
        self.assertRaises(KeyError, self.provider.registerService, str)
        self.assertTrue(str in self.provider)

    def test_registerWithArgs(self):
        o1, o2, o3, o4 = object(), object(), object(), object()
        self.provider.registerService(TestServiceClass, o1, o2, three = o3, four = o4)
        self.assertEquals(self.provider.getService(TestServiceClass).one, o1)
        self.assertEquals(self.provider.getService(TestServiceClass).two, o2)
        self.assertEquals(self.provider.getService(TestServiceClass).three, o3)
        self.assertEquals(self.provider.getService(TestServiceClass).four, o4)

    def test_registerWithOtherService(self):
        o1, o2, o3, o4, o5, o6, o7 = object(), object(), object(), object(), object(), object(), object()
        self.provider.registerService(TestServiceOtherClass, lookupService(TestServiceClass), o5, o6, o7)
        self.provider.registerService(TestServiceClass, o1, o2, o3, o4)
        self.assertTrue(self.provider.getService(TestServiceOtherClass).one.__class__ is TestServiceClass)
        self.assertEquals(self.provider.getService(TestServiceOtherClass).one.one, o1)
        self.assertEquals(self.provider.getService(TestServiceOtherClass).one.two, o2)
        self.assertEquals(self.provider.getService(TestServiceOtherClass).one.three, o3)
        self.assertEquals(self.provider.getService(TestServiceOtherClass).one.four, o4)
        self.assertEquals(self.provider.getService(TestServiceOtherClass).two, o5)
        self.assertEquals(self.provider.getService(TestServiceOtherClass).three, o6)
        self.assertEquals(self.provider.getService(TestServiceOtherClass).four, o7)

    def test_registerServiceNoOtherRegisteredError(self):
        self.provider.registerService(TestServiceClass, lookupService(TestServiceOtherClass))
        self.assertRaises(KeyError, self.provider.getService, TestServiceClass)
        self.assertRaises(KeyError, self.provider.getService, TestServiceOtherClass)

    def test_getNonExistingService(self):
        self.assertFalse(str in self.provider)
        self.assertRaises(KeyError, self.provider.getService, str)

class TestServiceClass(object):

    one = None
    two = None
    three = None
    four = None

    def __init__(self, one, two, three = None, four = None):
        self.one = one
        self.two = two
        self.three = three
        self.four = four

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        else:
            return id(self) == id(other)

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        else:
            return not result

class TestServiceOtherClass(TestServiceClass):
    pass
