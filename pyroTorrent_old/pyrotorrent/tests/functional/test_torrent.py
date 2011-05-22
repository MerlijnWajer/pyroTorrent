from pyrotorrent.tests import *

class TestTorrentController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='torrent', action='index'))
        # Test response...
