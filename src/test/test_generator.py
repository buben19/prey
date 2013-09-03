import twisted.trial.unittest
import ipaddr
try:
    import prey.src.generator as generator
except ImportError:
    import sys
    import os
    import os.path
    sys.path.append(os.path.join(os.getcwd(), ".."))
    import src.generator as generator

class TestRandomIPV4AddressGenerator(twisted.trial.unittest.TestCase):

    generator = None

    def setUp(self):
        self.generator = generator.RandomIPV4AddressGenerator()

    def tearDown(self):
        self.generator = None

    def test_generate(self):
        addr = ipaddr.IPAddress(self.generator.generate())
        self.assertEquals(addr.version, 4)

class TestValidIPV4AddressGenerator(twisted.trial.unittest.TestCase):

    generator = None

    def setUp(self):
        self.generator = generator.ValidIPV4AddressGenerator(generator.RandomIPV4AddressGenerator())

    def tearDown(self):
        self.generator = None

    def test_generate(self):
        addr = ipaddr.IPAddress(self.generator.generate())
        self.assertEquals(addr.version, 4)
