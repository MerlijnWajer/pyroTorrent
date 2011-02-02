"""

.. _torrentquery-class:

TorrentQuery
============

The Torrent query class can be used to send multiple queries over one
XMLRPC command, thus heavily decreasing loading times.

"""
from pyrotorrent.lib.multibase import MultiBase
from pyrotorrent.model import torrent

class TorrentQuery(MultiBase):
    """
        The Torrent query class can be used to send multiple queries over one
        XMLRPC command, thus heavily decreasing loading times.
    """

    def __init__(self, host, port=80, url='/RPC2', *args):
        """
        Pass the host, port, url and possible default arguments.
        *args is usually only the torrent hash or just undefined.
        """

        MultiBase.__init__(self, host, port, url, *args)
        self._rpc_methods = torrent._rpc_methods

