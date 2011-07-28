"""
.. _peer-class:

Peer
====

The Peer Model.

It took me some time to figure out what was initially wrong with the peer
multicall - http://libtorrent.rakshasa.no/ticket/1308. If only rtorrent had been
documented a *little* better.
"""

from lib.xmlrpc import RTorrentXMLRPC

class Peer(object):
    """
    Peer class.
    """

    # FIXME: If we leave URL at '' xmlrpclib will default to /RPC2 as well.
    def __init__(self):
        """
        Initialise the Peer object.
        """
        self.s = RTorrentXMLRPC()

import types

_rpc_methods = {
    'is_obfuscated' : ('p.is_obfuscated',
        """
        Returns if the client is obfuscated.
        """), # XXX: What is obfuscated in peer context?
    'is_snubbed' : ('p.is_snubbed',
        """
        """), # XXX: What is obfuscated in peer context?
    'is_encrypted' : ('p.is_encrypted',
        """
        Returns if the peer is encrypted.
        """),
    'is_incoming' : ('p.is_incoming',
        """
        Returns if the peer is an incoming peer.
        """),
    'get_address' : ('p.get_address',
        """
        Returns the IP address of the peer.
        """),
    'get_port' : ('p.get_port',
        """
        Returns the port of the peer.
        """),
    'get_client_version' : ('p.get_client_version',
        """
        Returns the client version string of the peer.
        """),
    'get_completed_percent' : ('p.get_completed_percent',
        """
        Returns the completed percent of the peer.
        """),
    'get_id' : ('p.get_id',
        """
        Returns the ID of the peer.
        """),
    'get_upload_rate' : ('p.get_up_rate',
        """
        Returns the upload rate of the peer.
        """),
    'get_upload_total' : ('p.get_up_total',
        """
        Returns the upload total of the peer.
        """),
    'get_download_rate' : ('p.get_down_rate',
        """
        Returns the download rate of the peer.
        """),
    'get_download_total' : ('p.get_down_total',
        """
        Returns the download total of the peer.
        """),
    'get_rate' : ('p.get_peer_rate',
        """
        """), # XXX: Rate?
    'get_total' : ('p.get_peer_total',
        """
        """) # XXX: Total?
}


for x, y in _rpc_methods.iteritems():
    caller = (lambda name: lambda self, *args: getattr(self.s, name)(*args))(y[0])
    caller.__doc__ = y[1] + '\nOriginal libTorrent method: ``%s``' % y[0]
    setattr(Peer, x, types.MethodType(caller, None, Peer))

    del caller
