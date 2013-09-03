import twisted.trial.unittest
import twisted.internet.defer
from .. import tools

class TestObjectMultiplier(twisted.trial.unittest.TestCase):

    multiplier = None

    def setUp(self):
        self.multiplier = tools.ObjectMultiplier()

    def tearDown(self):
        self.multiplier = None

    def test_my(self):
        pass
