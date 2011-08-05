"""
XMLRPCLib Wrapper with support for SCGI over unix:// and network(ed) sockets.
(Also supports http://)
"""

import xmlrpclib
import xmlrpc2scgi

from config_parser import CONNECTION_HTTP, CONNECTION_SCGI

class RTorrentXMLRPCException(Exception):
    pass

class RTorrentXMLRPC(object):

    def __init__(self, target):
        self.info = target

        if self.info['type'] == CONNECTION_HTTP:
            self.c = xmlrpclib.ServerProxy('http://%s:%i%s' % \
                (self.info['host'], self.info['port'], \
                self.info['url']))
        else:
            self.c = xmlrpc2scgi.RTorrentXMLRPCClient(self.info['fd'])


    def __getattr__(self, attr, **args):
        return getattr(self.c, attr)
