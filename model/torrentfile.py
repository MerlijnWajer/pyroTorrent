"""
.. _torrentfile-class:

TorrentFile
===========

"""

from lib.xmlrpc import RTorrentXMLRPC
import types

class TorrentFile(object):
    """
    """

    def __init__(self, target):

        self.target = target
        self.s = RTorrentXMLRPC(target)

    def query(self):
        """
        """
        raise Exception('TODO')

_rpc_methods = {
    'get_path' : ('f.get_path',
        """
        Returns the path.
        """),
    'get_path_components' : ('f.get_path_components',
        """
        Returns the path components.
        """),
    'get_frozen_path' : ('f.get_frozen_path',
        """
        Returns the *frozen* path.
        """), # XXX: What is the frozen path?
    'get_size_bytes' : ('f.get_size_bytes',
        """
        Returns the total size of the file.
        """),
    'get_size_chunks' : ('f.get_size_chunks',
        """
        Returns the size of the file in chunks.
        """),
    'get_completed_chunks' : ('f.get_completed_chunks',
        """
        Get the amount of completed chunks.
        """)
        }

for x, y in _rpc_methods.iteritems():
    caller = (lambda name: lambda self, *args: getattr(self.s, name)(self._hash, *args))(y[0])
    caller.__doc__ = y[1]
    setattr(TorrentFile, x, types.MethodType(caller, None, TorrentFile))

    del caller
