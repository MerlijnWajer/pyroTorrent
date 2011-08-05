"""
.. _peerrequester-class:

PeerRequester
================
"""
# Also change return type? not list of list but perhaps a dict or class?
# Properly implement flush?

import xmlrpclib
from model import peer
from lib.baserequester import BaseRequester, InvalidTorrentCommandException

class PeerRequester(BaseRequester):
    """
    """
    def __init__(self, target, *first_args):
        BaseRequester.__init__(self, target)
        self.first_args = first_args

    def dofetch(self, *rpc_commands):
        return self.s.p.multicall(*(self.first_args + (' ',) + rpc_commands))

    def _convert_command(self, command):
        """
        Convert command based on torrent._rpc_methods to rtorrent command.
        """
        if command in peer._rpc_methods:
            return peer._rpc_methods[command][0]
        else:
            raise InvalidTorrentCommandException("%s is not a valid command" %
                    command)

