from pyrotorrent.lib.multibase import MultiBase
from pyrotorrent.model import torrent

class TorrentQuery(MultiBase):

    def __init__(self, host, port=80, url='/RPC2', *args):
        """
        """

        MultiBase.__init__(self, host, port, url, *args)
        self._rpc_methods = torrent._rpc_methods

