"""
XMLRPCLib Wrapper with support for SCGI over unix:// and network(ed) sockets.
(Also supports http://)
"""

import xmlrpclib
import xmlrpc2scgi

from config import rtorrent_config

CONNECTION_SCGI, CONNECTION_HTTP = range(2)

class RTorrentXMLRPCException(Exception):
    pass

class RTorrentXMLRPC(object):

    def __init__(self):
        self.info = self._parse_config()

        if self.info['type'] == CONNECTION_HTTP:
            self.c = xmlrpclib.ServerProxy('http://%s:%i%s' % \
                (self.info['host'], self.info['port'], self.info['url']))
        else:
            self.c = xmlrpc2scgi.RTorrentXMLRPCClient(self.info['fd'])

    def _parse_config(self):
        if 'scgi' in rtorrent_config and 'http' in rtorrent_config:
            raise RTorrentXMLRPCException('Ambigious configuration')

        if 'scgi' in rtorrent_config:
            if 'unix-socket' in rtorrent_config['scgi']:
                # TODO: Check path
                return \
                {
                    'type' : CONNECTION_SCGI,
                    'fd' : 'scgi://%s' % rtorrent_config['scgi']['unix-socket']
                }
            elif 'host' in rtorrent_config['scgi'] and \
                 'port' in rtorrent_config['scgi']:
                return \
                {
                    'type' : CONNECTION_SCGI,
                    'fd' : 'scgi://%s:%d' % (rtorrent_config['scgi']['host'], \
                                             rtorrent_config['scgi']['port'])
                }
            else:
                raise RTorrentXMLRPCException('Config lacks specific scgi'
                    'information. Needs host and port or unix-socket.')

        elif 'http' in rtorrent_config:
            return \
            {
                'type' : CONNECTION_HTTP,
                'host' : rtorrent_config['http']['host'],
                'port' : rtorrent_config['http']['port'],
                'url' :  rtorrent_config['http']['url']
            }
        else:
            raise RTorrentXMLRPCException('Config lacks scgi of http'
                    'information')

    def __getattr__(self, attr):
        return getattr(self.c, attr)
