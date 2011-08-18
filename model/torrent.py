#!/usr/bin/python
"""
.. _torrent-class:

Torrent
=======

The Torrent class defines a single torrent.
It is instantiated with a Torrent specific hash,
and connection information similar to :ref:`rtorrent-class`.
"""

from lib.xmlrpc import RTorrentXMLRPC
import types

#from lib.peerrequester import PeerRequester

class Torrent(object):
    """
    Torrent class. This class contains most of the methods specific to a
    torrent, such as get_name, get_hash, is_complete, get_download_rate, etc.
    """

    def __init__(self, target, _hash):
        """
        Initialise the Torrent object; pass a target dict (parsed by
        parse_config in pyrotorrentpy) and the torrent hash.
        """
        self.target = target
        self.s = RTorrentXMLRPC(target)
        self._hash = _hash

    def __repr__(self):
        return 'Torrent(%s): %s' % (self._hash, self.get_name())

    def query(self):
        """
        Query returns a new TorrentQuery object with the host, port, url and
        hash(!) from the current Torrent object. The hash will be used as
        default argument in the TorrentQuery class.
        See :ref:`torrentquery-class`
        """
        from lib.torrentquery import TorrentQuery
        return TorrentQuery(self.target, self._hash)

    def get_peers(self):
        pass

# XXX: Begin hacks

# RPC Methods for Torrent. You don't have to pass the Torrent hash; it is
# automatically passed. When you invoke one of these methods on a Torrent
# instance.
_rpc_methods = {
    'get_name' : ('d.get_name', # XXX: get_base_filename is the same?
        """
        Returns the name of the Torrent.
        """),
    'get_full_path' : ('d.get_base_path',
        """
        Returns the full path to the Torrent.
        """),
    'get_bytes_done' : ('d.get_bytes_done',
        """
        Returns the amount of bytes done.
        """),
    'is_complete' : ('d.get_complete',
        """
        Returns 1 if torrent is complete; 0 if it is not complete.
        """),
    'get_download_rate' : ('d.get_down_rate',
        """
        Returns the current download rate for Torrent.
        """),
    'get_download_total' : ('d.get_down_total',
        """
        Returns the total downloaded data for torrent.
        """),
    'get_upload_rate' : ('d.get_up_rate',
        """
        Returns the current upload rate for Torrent.
        """),
    'get_upload_total' : ('d.get_up_total',
        """
        Returns the total uploaded data for torrent.
        """),
    'get_bytes_left' : ('d.get_left_bytes',
        """
        Returns the amounts of bytes left to download.
        """),
    'get_ratio' : ('d.get_ratio',
        """
        Returns the ratio for this Torrent. (Download / Upload)
        """),
    'get_size_bytes' : ('d.get_size_bytes',
        """
        Returns the size of the torrent in bytes.
        """),
    'get_size_chucks' : ('d.get_size_chucks',
        """
        Returns the size of the torrent in chucks.
        """),
    'get_size_files' : ('d.get_size_files',
        """
        Returns the size of the torrent in files.
        """),
    'get_loaded_file' : ('d.get_loaded_file',
        """
        Returns absolute path to .torrent file.
        """),

    'get_hash' :  ('d.get_hash',
        """
        Returns the torrent hash. Very useful.
        """),
    'is_hashing' : ('d.get_hashing',
        """
        """),
    'hashing_failed' : ('d.get_hashing_failed',
        """
        """),
    'perform_hash_check' : ('d.check_hash',
        """
        Performs a hash check. Returns 0 immediately.
        """),
    'open' : ('d.open',
        """
        Open a torrent.
        """),
    'close' : ('d.close',
        """
        Close a torrent.
        """),
    'start' : ('d.start',
        """
        Start a torrent.
        """),
    'stop' : ('d.stop',
        """
        Stop a torrent.
        """),
    'pause' : ('d.pause',
        """
        Pause a torrent.
        """),
    'resume' : ('d.resume',
        """
        Resume a torrent.
        """),
    'erase' : ('d.erase',
        """
        Erase a torrent.
        """),
    'is_active' : ('d.is_active',
        """
        Returns 1 if the torrent is active; 0 when it is not active.

        XXX: As of yet we're not completely sure what ``active'' means.
        """),
    'is_open' : ('d.is_open',
        """
        Returns 1 if the torrent is open, 0 otherwise.
        """
        ),
    'is_hash_checked' : ('d.is_hash_checked',
        """
        Returns 1 if the hash has been checked, 0 is otherwise.
        """),
    'is_hash_checking' : ('d.is_hash_checking',
        """
        Returns 1 if the hash is currently being checked, 0 otherwise?
        TODO
        """), # TODO
    'get_state' : ('d.get_state',
        """
        No clue as to what this returns yet.
        TODO
        """),# TODO
    'get_message' : ('d.get_message',
        """
        Returns the torrent *message*.
        """),
    'get_views' : ('d.views',
        """
        """)
}

for x, y in _rpc_methods.iteritems():

    # Passing self._hash as first (default) argument. This may be easier in
    # most cases. If you don't want to pass a default (hash) argument; use the
    # _rpc_methods_noautoarg variable.

    #caller = (lambda name: lambda self, *args: getattr(self.s, name)(*args))(y[0])

    caller = (lambda name: lambda self, *args: getattr(self.s, name)(self._hash, *args))(y[0])
    caller.__doc__ = y[1] + '\nOriginal libTorrent method: ``%s``' % y[0]
    setattr(Torrent, x, types.MethodType(caller, None, Torrent))

    del caller
