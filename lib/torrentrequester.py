"""
.. _torrentrequester-class:

TorrentRequester
================

The TorrentRequester is a class created to quickly and efficiently query all the
torrents in a view. It only uses one XMLRPC request. All the methods you can
perform on TorrentRequester are identical to the methods on
:ref:`torrent-class`. (Although set* methods have not been implemented)

Example usage:

.. code-block:: python

    t = TorrentRequester('hostname')
    t.get_name().get_hash() # Chaining commands is possible
    t.get_upload_throttle() # As well as calling another method on it.
    print t.all()

"""
# Also change return type? not list of list but perhaps a dict or class?
# Properly implement flush?

import xmlrpclib
from model import torrent
from lib.baserequester import BaseRequester

from config import *

class TorrentRequester(BaseRequester):
    """
    """
    def __init__(self, *first_args):
        BaseRequester.__init__(self, **rtorrent_config)
        self.first_args = first_args

    def dofetch(self, *rpc_commands):
        return self.s.d.multicall(*(self.first_args + rpc_commands))

    def _convert_command(self, command):
        """
        Convert command based on torrent._rpc_methods to rtorrent command.
        """
        if command in torrent._rpc_methods:
            return torrent._rpc_methods[command][0]
        else:
            raise InvalidTorrentCommandException("%s is not a valid command" %
                    command)

if __name__ == '__main__':

    t = TorrentRequester('192.168.1.75')
    t.get_name().get_hash().get_name()
    for x in t.all():
        print x


