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

    """

    def __init__(self, host, port=80):
        # No ending '/' !
        self.s = xmlrpclib.ServerProxy('http://%s:%i' % (host, port))

    def get_upload_rate(self):
        return self.s.get_upload_rate()

    def set_upload_rate(self, rate):
        # If invalid, raise ValueError.
        rate = int(rate)
        return self.s.set_upload_rate(rate)

if __name__ == '__main__':
    r = RTorrent('sheeva')

    print r.get_upload_rate()


