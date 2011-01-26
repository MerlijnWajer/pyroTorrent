#!/usr/bin/python
"""
.. _rtorrent-class:

The RTorrent class serves as an interface to a remote RTorrent (program?).
It implements a lot of the functionality that RTorrent exposes over XMLRPC;
currently only XMLRPC over HTTP is supported; but support for direct SCGI is
planned. Basically, HTTP support requires a web server to direct requests to
RTorrent, whereas SCGI talks directly to RTorrent. (The web server also uses
SCGI to talk to RTorrent)

Some of the functions documented in here are in fact auto generated (on the
fly); they will only have one argument: *args.
Obviously some do not take any arguments; the docstring should
(in the near future, anyway) explain exactly what variables
should be passed.
"""

# TODO:  SCGI support (with xmlrpc2scgi.py from rtorrent wiki)

import xmlrpclib

class RTorrent(object):
    """
    RTorrent class. This wraps most of the RTorrent *main* functionality
    (read: global functionality) in a class.
    Methods specific to a Torrent can be found in the :ref:`torrent-class`
    class.
    """

    # FIXME: If we leave URL at '' xmlrpclib will default to /RPC2 as well.
    def __init__(self, host, port=80, url='/RPC2'):
        """
        Initialise the RTorrent object.
        Host is the hostname of the server where the XMLRPC interface is
        running. (HTTP only at the moment)
        Port is the port for http...
        URL defaults to '/RPC2', you shouldn't change this unless you know
        what you are doing.
        """
        # No ending '/' !
        self.s = xmlrpclib.ServerProxy('http://%s:%i%s' % (host, port, url))

    def get_download_list(self, _type=''):
        """
        Returns a list of torrents.
        _type defines what is returned. Valid:
            *   '' (Empty string)
            *   'complete'
            *   'incomplete'
            *   'started'
            *   'stopped'
            *   'active'
            *   'hashing'
            *   'seeding'
        """
        # FIXME: List is not complete(?) + exception should be raised.
        if _type not in ('complete', 'incomplete', 'started', 'stopped',
                'active', 'hashing', 'seeding', ''):
            return None

        res = self.s.download_list(_type)

        # FIXME: We now only have the hashes. Do we also want to fetch all the
        # data per torrent? Or perhaps only the basic info?

        return res


# XXX: Begin hacks

import types

_rpc_methods = {
    'get_upload_throttle' : ('get_upload_rate',
        """
        Returns the current upload throttle.
        """),
    'set_upload_throttle' : ('set_upload_rate',
        """
        Set the current upload throttle.
        Pass the new throttle size in bytes.
        """),
    'get_download_throttle' : ('get_download_rate',
        """
        Returns the download upload throttle.
        """),
    'set_download_throttle' : ('set_download_rate',
        """
        Set the current download throttle.
        Pass the new throttle size in bytes.
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


# A quick and dirty attempt at implementing ``argument-checking'' as well.
# It probably wouldn't really allow all the checking one would really want, and
# I doubt we'll need it too.

#def ex():
#    raise Exception('jeej')
#
#def create_caller(name, arg_check):
#    return lambda self, *args: getattr(self.s, name)(*args) if arg_check(*args) else ex()
#
#def create_argcheck(arg_valid):
#    return lambda *args: len(args) == len(arg_valid) \
#        and all(map(lambda x, y: type(x) is y, args, arg_valid)) 

# Hack in all the methods in _rpc_methods!
for x, y in _rpc_methods.iteritems():

#   caller = create_caller(y[0], create_argcheck(y[2])) # belongs to the
#   argument checking

    caller = (lambda name: lambda self, *args: getattr(self.s, name)(*args))(y[0])
    caller.__doc__ = y[1]
    setattr(RTorrent, x, types.MethodType(caller, None, RTorrent))

# XXX: End hacks


if __name__ == '__main__':
    x = RTorrent('sheeva')

    # Simple test.
    old = x.get_upload_throttle()
    print 'Throttle:', old
    print 'Return:', x.set_upload_throttle(20000)
    print 'Throttle:', x.get_upload_throttle()
    print 'Return:', x.set_upload_throttle(old)
    print 'Throttle:', x.get_upload_throttle()

    print 'Download list', x.get_download_list()
