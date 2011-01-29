# Also change return type? not list of list but perhaps a dict or class?

import xmlrpclib
from model import torrent

class InvalidTorrentCommandException(Exception):
    pass

class TorrentRequester(object):

    def __init__(self, host, port=80, url='/RPC2'):
        self.s = xmlrpclib.ServerProxy('http://%s:%i%s' % (host, port, url))
        self.host, self.port, self.url = host, port, url
        self.commandstack = []
        self.commands = {}

    def __call__(self, *args):
        """
        Return self so we can chain calls:
        >>> t.get_name().get_hash()
        """
        if len(args):
            raise InvalidTorrentCommandException('No parameters are supported'\
                'yet')
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

    def _fetch(self):
        """
        Executes the current command stack. Stores results in the class.
        """
        rpc_commands = []
        for x in self.commandstack:
            rpc_commands.append('%s=' % x)
            if len(self.commands[x]):
                pass # TODO: Add args for set*

        self.__res = self.s.d.multicall('', *rpc_commands)

    def all(self):
        """
        Returns a list of the results.
        """
        self._fetch()
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
        command = self._convert_command(command)

        self.commands[command] = ()
        self.commandstack.append('%s' % command)

    # XXX: When do we use this? Do we use it all? Do we need it at all?
    # Do we have it here just as a convenience for the user?
    def flush(self):
        del self.commandsstack
        del self.commands
        self.commandsstack = []
        self.commands = {}

if __name__ == '__main__':

    t = TorrentRequester('192.168.1.75')
    t.get_name().get_hash().get_name()
    for x in t.all():
        print x
#    print t.all()


