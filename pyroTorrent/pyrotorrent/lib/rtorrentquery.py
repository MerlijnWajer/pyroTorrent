"""

.. _rtorrentquery-class:

RTorrentQuery
=============

The RTorrent query class can be used to send multiple queries over one
XMLRPC command, thus heavily decreasing loading times.

It is created in RTorrent.query() or can be manually created using the
RTorrentQuery() constructor.
"""
from pyrotorrent.lib.multibase import MultiBase
from pyrotorrent.model import rtorrent

class RTorrentQuery(MultiBase):
    """
        The RTorrent query class can be used to send multiple queries over one
        XMLRPC command, thus heavily decreasing loading times.
    """

    def __init__(self, host, port=80, url='/RPC2', *args):
        """
        Pass the host, port, url and possible default arguments.
        """

        MultiBase.__init__(self, host, port, url, *args)
        self._rpc_methods = rtorrent._rpc_methods

