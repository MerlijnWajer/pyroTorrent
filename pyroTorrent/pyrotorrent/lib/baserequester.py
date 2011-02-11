import xmlrpclib

class BaseRequester(object):
    """
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

    def _fetch(self):
        """
        Executes the current command stack. Stores results in the class.
        """
        rpc_commands = []
        for x in self.commandstack:
            rpc_commands.append('%s=' % x)
            if len(self.commands[x]):
                pass # TODO: Add args for set*

        res = self.dofetch(*rpc_commands)
        print 'cs', self.commandistack
        print 'res0', res[0]

        self.__res = [DictAttribute(zip(self.commandistack, x)) for x in res]

    def all(self):
        """
        Returns a list of the results.
        """
        self._fetch()
        return self.__res

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

