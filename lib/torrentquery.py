"""

.. _torrentquery-class:

TorrentQuery
============

The Torrent query class can be used to send multiple queries over one
XMLRPC command, thus heavily decreasing loading times.

"""
from lib.multibase import MultiBase
from model import torrent

class TorrentQuery(MultiBase):
    """
        The Torrent query class can be used to send multiple queries over one
        XMLRPC command, thus heavily decreasing loading times.
    """

    def __init__(self, *args):
        """
        Pass the host, port, url and possible default arguments.
        *args is usually only the torrent hash or just undefined.
        """

        MultiBase.__init__(self, *args)
        self._rpc_methods = torrent._rpc_methods

