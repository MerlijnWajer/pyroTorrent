from pyrotorrent.tests import *

class TestPyroController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='pyro', action='index'))
        # Test response...
