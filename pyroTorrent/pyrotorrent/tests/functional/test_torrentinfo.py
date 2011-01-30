from pyrotorrent.tests import *

class TestTorrentinfoController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='torrentinfo', action='index'))
        # Test response...
