from pyrotorrent.lib.multibase import MultiBase
from pyrotorrent.model import rtorrent

class RTorrentQuery(MultiBase):

    def __init__(self, host, port=80, url='/RPC2', *args):
        """
        """

        MultiBase.__init__(self, host, port, url, *args)
        self._rpc_methods = rtorrent._rpc_methods

