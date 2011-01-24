#!/usr/bin/python
"""
RTorrent class.

Supported protocols:
    -   HTTP
To support:
    -   SCGI (with xmlrpc2scgi.py from rtorrent wiki)
"""

import xmlrpclib

class RTorrent(object):
    """
    RTorrent class.


    """

    def __init__(self, host, port=80, url='/RPC2'):
        # No ending '/' !
        self.s = xmlrpclib.ServerProxy('http://%s:%i%s' % (host, port, url))


# XXX: Begin hacks

import types

_rpc_methods = {
    'get_upload_throttle' : ('get_upload_rate',
        """
        Returns the current upload throttle.
        """),
    'set_upload_throttle' : ('set_upload_rate',
        """
        Set the current upload throttle. (In bytes)
        """),
    'get_download_throttle' : ('get_download_rate',
        """
        Returns the download upload throttle.
        """),
    'set_download_throttle' : ('set_download_rate',
        """
        Set the current download throttle. (In bytes)
        """),
    'get_upload_rate' : ('get_up_rate',
        """
        Returns the current upload rate.
        """),
    'get_upload_rate_total' : ('get_up_total',
        """
        Returns the total uploaded data.
        """), # XXX ^ Unsure about comment
    'get_download_rate' : ('get_down_rate',
        """
        Returns the current download rate.
        """),
    'get_download_rate_total' : ('get_down_total',
        """
        Returns the total downloaded data.
        """) # XXX ^ Unsure about comment
}

# Hack in all the methods in _rpc_methods!

for x, y in _rpc_methods.iteritems():
    caller = (lambda name: lambda self, *args: getattr(self.s, name)(*args))(y[0])
    caller.__doc__ = y[1]
    setattr(RTorrent, x, types.MethodType(caller, None, RTorrent))

#   Old hack:
#    exec('caller = lambda self, *args: getattr(self.s, \''+y+'\')(*args)')

# XXX: End hacks


if __name__ == '__main__':
    x = RTorrent('sheeva')

    old = x.get_upload_throttle()
    print 'Throttle:', old
    print 'Return:', x.set_upload_throttle(20000)
    print 'Throttle:', x.get_upload_throttle()
    print 'Return:', x.set_upload_throttle(old)
    print 'Throttle:', x.get_upload_throttle()

