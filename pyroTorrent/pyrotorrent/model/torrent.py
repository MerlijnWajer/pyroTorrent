#!/usr/bin/python
"""
.. _torrent-class:

Torrent
=======

The Torrent class defines a single torrent.
It is instantiated with a Torrent specific hash, 
and connection information similar to :ref:`rtorrent-class`.
"""

import xmlrpclib

class Torrent(object):
    """
    """

    def __init__(self, _hash, host, port=80, url='/RPC2'):
        self._hash = _hash
        self.s = xmlrpclib.ServerProxy('http://%s:%i%s' % (host, port, url))
        self.host, self.port, self.url = host, port, url

# XXX: Begin hacks

import types

# RPC Methods for Torrent. You don't have to pass the Torrent hash; it is
# automatically passed. When you invoke one of these methods on a Torrent
# instance.
_rpc_methods = {
    'get_name' : ('d.get_name', # XXX: get_base_filename is the same?
        """
        Returns the name of the Torrent.
        """),
    'get_full_path' : ('d.get_get_path',
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

    'perform_hash_check' : (' d.check_hash',
        """
        Performs a hash check. Returns 0 immediately.
        Unsure how to get the result of the hash check, ATM.
        """)


}

# RPC Methods for Torrent. These do not pass any argument automatically. (See
# above comments)
_rpc_methods_noautoarg = {

}

for x, y in _rpc_methods.iteritems():

    # Passing self._hash as first (default) argument. This may be easier in
    # most cases. If you don't want to pass a default (hash) argument; use the
    # _rpc_methods_noautoarg variable.

    #caller = (lambda name: lambda self, *args: getattr(self.s, name)(*args))(y[0])

    caller = (lambda name: lambda self, *args: getattr(self.s, name)(self._hash, *args))(y[0])
    caller.__doc__ = y[1]
    setattr(Torrent, x, types.MethodType(caller, None, Torrent))

    del caller

for x, y in _rpc_methods_noautoarg.iteritems():

    caller = (lambda name: lambda self, *args: getattr(self.s, name)(*args))(y[0])
    caller.__doc__ = y[1]
    setattr(Torrent, x, types.MethodType(caller, None, Torrent))

    del caller

# XXX: End hacks

if __name__ == '__main__':
    t = Torrent('0D4E955B2341EB065836AE1972C4282708886506', 'sheeva')

    print t.get_name()
