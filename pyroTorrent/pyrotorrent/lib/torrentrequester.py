"""
.. _torrentrequester-class:

TorrentRequester
================
"""
# Also change return type? not list of list but perhaps a dict or class?

import xmlrpclib
from pyrotorrent.model import torrent

class TorrentRequester(object):
    """
    The TorrentRequester is FIXME COMPLETE
    """
    def __init__(self, host, port=80, url='/RPC2'):
        """
        """
        self.s = xmlrpclib.ServerProxy('http://%s:%i%s' % (host, port, url))
        self.host, self.port, self.url = host, port, url

        # Stack to put commands on
        self.commandstack = []

        # Same as commandstack, but stores the original names.
        # We need to for .all()
        self.commandistack = []

        # Contains possible arguments.
        self.commands = {}

    def __call__(self, *args):
        """
        Return self so we can chain calls:

        .. code-block:: python

            t = TorrentRequester('hostname')
            t.get_name().get_hash() # Chaining
            print t.all()
        """
        if len(args):
            raise InvalidTorrentCommandException('No parameters are supported' \
                ' yet')
        self.commands[self.commandstack[-1]] = args
        return self

    def __getattr__(self, attr):
        """
        Used to add commands.
        """
        try:
            self.append_command(attr)
        except InvalidTorrentCommandException, e:
            raise AttributeError(e.message)
        return self

    def _fetch(self, model):
        """
        Executes the current command stack. Stores results in the class.
        """
        # TODO: Verify model?
        rpc_commands = []
        for x in self.commandstack:
            rpc_commands.append('%s=' % x)
            if len(self.commands[x]):
                pass # TODO: Add args for set*

        res = self.s.d.multicall(model, *rpc_commands)

        self.__res = [DictAttribute(zip(self.commandistack, x)) for x in res]

    def all(self, model=''):
        """
        Returns a list of the results.
        """
        self._fetch(model)
        return self.__res

    def _convert_command(self, command):
        """
        Convert command based on torrent._rpc_methods to rtorrent command.
        """
        if command in torrent._rpc_methods:
            return torrent._rpc_methods[command][0]
        else:
            raise InvalidTorrentCommandException("%s is not a valid command" %
                    command)

    def append_command(self, command):
        """
        Add commands to the stack.
        """
        # TODO: Find out how set commands work.
        oldcommand = command
        command = self._convert_command(command)

        self.commands[command] = ()
        self.commandstack.append(command)
        self.commandistack.append(oldcommand)

    # XXX: When do we use this? Do we use it all? Do we need it at all?
    # Do we have it here just as a convenience for the user?
    def flush(self):
        del self.commandsstack
        del self.commands
        self.commandsstack = []
        self.commandisstack = []
        self.commands = {}

class InvalidTorrentCommandException(Exception):
    """
    Thrown on an invalid command.
    """

class DictAttribute(dict):
    def __getattr__(self, attr):
        if attr in self:
            return self[attr]
        else:
            raise AttributeError('%s not in dict' % attr)

if __name__ == '__main__':

    t = TorrentRequester('192.168.1.75')
    t.get_name().get_hash().get_name()
    for x in t.all():
        print x


