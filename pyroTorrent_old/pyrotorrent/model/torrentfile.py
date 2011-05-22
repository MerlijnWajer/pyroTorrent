"""
.. _torrentfile-class:

TorrentFile
===========

"""

import xmlrpclib
import types

class TorrentFile(object):
    """
    """

    def query(self):
        """
        """

_rpc_methods = {
    'get_path' : ('f.get_path',
        """
        Returns the path.
        """), # XXX: What is the frozen path?
    'get_path_components' : ('f.get_path_components',
        """
        Returns the path components.
        """), # XXX: What is the frozen path?
    'get_frozen_path' : ('f.get_frozen_path',
        """
        Returns the *frozen* path.
        """), # XXX: What is the frozen path?
    'get_size_bytes' : ('f.get_size_bytes',
        """
        Returns the total size of the file.
        """)
        }

for x, y in _rpc_methods.iteritems():

    # Passing self._hash as first (default) argument. This may be easier in
    # most cases. If you don't want to pass a default (hash) argument; use the
    # _rpc_methods_noautoarg variable.

    #caller = (lambda name: lambda self, *args: getattr(self.s, name)(*args))(y[0])

    caller = (lambda name: lambda self, *args: getattr(self.s, name)(self._hash, *args))(y[0])
    caller.__doc__ = y[1]
    setattr(TorrentFile, x, types.MethodType(caller, None, TorrentFile))

    del caller
