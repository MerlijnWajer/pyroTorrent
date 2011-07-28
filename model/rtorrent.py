"""
.. _rtorrent-class:

RTorrent
========

The RTorrent class serves as an interface to a remote RTorrent (program?).
It implements a lot of the functionality that RTorrent exposes over XMLRPC;
currently only XMLRPC over HTTP is supported; but support for direct SCGI is
planned. Basically, HTTP support requires a web server to direct requests to
RTorrent, whereas SCGI talks directly to RTorrent. (The web server also uses
SCGI to talk to RTorrent)

The RTorrent constructor requires a host and optionally a port and url.

Some of the functions documented in here are in fact auto generated (on the
fly); We did this for a few reasons: extendability and ease of use. (We can
easily chain calls this way)
They will only have one argument in the documentation: *args.
Obviously some do not take any arguments; the docstring should
(in the near future, anyway) explain exactly what variables
should be passed.

A simple test:

.. code-block: python


    x = RTorrent('sheeva')

    # Simple test.
    old = x.get_upload_throttle()
    print 'Throttle:', old
    print 'Return:', x.set_upload_throttle(20000)
    print 'Throttle:', x.get_upload_throttle()
    print 'Return:', x.set_upload_throttle(old)
    print 'Throttle:', x.get_upload_throttle()

    print 'Download list', x.get_download_list()
"""

from lib.xmlrpc import RTorrentXMLRPC

class RTorrent(object):
    """
    RTorrent class. This wraps most of the RTorrent *main* functionality
    (read: global functionality) in a class. Think of, current upload and
    download, libTorrent version.


    Methods specific to a Torrent can be found in the :ref:`torrent-class`
    class.
    """

    # FIXME: If we leave URL at '' xmlrpclib will default to /RPC2 as well.
    def __init__(self):
        """
        Initialise the RTorrent object.
        Host is the hostname of the server where the XMLRPC interface is
        running. (HTTP only at the moment)
        Port is the port for http...
        URL defaults to '/RPC2', you shouldn't change this unless you know
        what you are doing.
        """

        self.s = RTorrentXMLRPC()

    def get_download_list(self, _type=''):
        """
        Returns a list of torrents.
        _type defines what is returned. Valid:

            *   '' (Empty string), 'default'
            *   'complete'
            *   'incomplete'
            *   'started'
            *   'stopped'
            *   'active'
            *   'hashing'
            *   'seeding'

        Plus all custom defined views.
        """
        # FIXME: List is not complete(?) + exception should be raised.
        if _type not in ('complete', 'incomplete', 'started', 'stopped',
                'active', 'hashing', 'seeding', '', 'default'):
            return None

        res = self.s.download_list(_type)

        # FIXME: We now only have the hashes. Do we also want to fetch all the
        # data per torrent? Or perhaps only the basic info?

        return res

    def query(self):
        """
        Query returns a new RTorrentQuery object with the host, port, url and
        hash from the current RTorrent object.

        Use this to execute several (different) calls on the RTorrent class in
        one request. This can increase performance and reduce latency and load.

        See :ref:`rtorrentquery-class` on how to use it.
        """
        from lib.rtorrentquery import RTorrentQuery
        return RTorrentQuery()

# XXX: Begin hacks

import types

_rpc_methods = {
    'get_upload_throttle' : ('get_upload_rate',
        """
        Returns the current upload throttle.
        """),
    'set_upload_throttle' : ('set_upload_rate',
        """
        Set the upload throttle.
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
        """), # XXX ^ Unsure about comment
    'get_memory_usage' : ('get_memory_usage',
        """
        Returns rtorrent memory usage.
        """),
    'get_max_memory_usage' : ('get_max_memory_usage',
        """
        Returns rtorrent maximum memory usage.
        """),
    'get_libtorrent_version' : ('system.library_version',
        """
        Returns the libtorrent version.
        """),
    'get_hostname' : ('system.hostname',
        """
        Returns the hostname.
        """),
    'add_torrent' : ('load',
        """
        Loads a torrent into rtorrent from the torrent path.
        """),
    'add_torrent_start' : ('load_start',
        """
        Loads a torrent into rtorrent from the torrent path.
        Will also start the download immediately.
        """),
    'add_torrent_raw' : ('load_raw',
        """
        Loads a torrent into rtorrent from a given string.
        """),
    'add_torrent_raw' : ('load_raw_start',
        """
        Loads a torrent into rtorrent from a given string.
        Will also start the download immediately.
        """),
    'get_ip' : ('get_ip',
        """
        Returns the IP rtorrent is bound to. (For XMLRPC?)
        """), # XXX:For XMLRPC? ^
    'get_view_list' : ('view_list',
        """
        Returns a list of all views.
        """),
    'create_view' : ('view_add',
        """
        Creates a view; requires a single argument: A name for the view.
        WARNING: If you add an already existing view; rtorrent will simply crash
        (at least 0.8.6 does).
        """)
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
    caller.__doc__ = y[1] + '\nOriginal libTorrent method: ``%s``' % y[0]
    setattr(RTorrent, x, types.MethodType(caller, None, RTorrent))

    del caller
