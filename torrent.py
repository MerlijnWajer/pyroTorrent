#!/usr/bin/python
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

_rpc_methods = {
    'get_name' : ('d.get_name',
        """
        Returns the name of the Torrent.
        """)
}

for x, y in _rpc_methods.iteritems():


    # XXX: Passing self._hash as first (default) argument. This may be easier in
    # most cases, it does kind of restrict the range of functions we can use.
    # We could always make two lists of methods. One where we always pass
    # self._hash as default argument, and one where we don't.

    #caller = (lambda name: lambda self, *args: getattr(self.s, name)(*args))(y[0])

    caller = (lambda name: lambda self, *args: getattr(self.s, name)(self._hash, *args))(y[0])
    caller.__doc__ = y[1]
    setattr(Torrent, x, types.MethodType(caller, None, Torrent))

    del caller

# XXX: End hacks

if __name__ == '__main__':
    t = Torrent('0D4E955B2341EB065836AE1972C4282708886506', 'sheeva')

    print t.get_name()
