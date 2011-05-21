"""
XMLRPCLib Wrapper with support for SCGI over unix:// and network(ed) sockets.
(Also supports http://)
"""

class XMLRPCWrapException(Exception):
    pass

class XMLRPCWrap(object):

    def __init__(self):
        pass

    def __getattr__(self, attr):
        return getattr(self._handler, attr)
