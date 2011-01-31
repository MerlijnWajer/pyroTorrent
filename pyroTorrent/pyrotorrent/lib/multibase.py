
import xmlrpclib

class MultiBase(object):
    """
    """

    def __init__(self, host, port=80, url='/RPC2'):
        """
        """
        self.s = xmlrpclib.ServerProxy('http://%s:%i%s' % (host, port, url))
        self.m = xmlrpclib.MultiCall(self.s)

        self.host, self.port, self.url = host, port, url

        # Stack to put commands on
        self.commandstack = []

    def __call__(self, attr, *args):
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
        _attr = self._convert_command(attr)
        getattr(self.m, _attr)(*args)
        self.commands.append(attr)
        
        return self

    def __getattr__(self, attr):
        """
        Used to add commands.
        """

        return lambda *args: self(attr, *args)

    def _fetch(self, model=''):
        """
        Executes the current command stack. Stores results in the class.
        """
        #res = self.m()

        def iterate(m):
            for x in m:
                yield AttributeDictMultiResult(zip(self.commandstack, x))
        return iterate(self.m())
        #return [AttributeDictMultiResult(zip(self.commandstack, x)) for x in res]

    def all(self, model=''):
        """
        Returns a list of the results.
        """
        return self._fetch('')

    def _convert_command(self, command):
        """
        Convert command based on self._rpc_methods to rtorrent command.
        """
        if command in self._rpc_methods:
            return self._rpc_methods[command][0]
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

        self.commandstack.append(command)

    # XXX: When do we use this? Do we use it all? Do we need it at all?
    # Do we have it here just as a convenience for the user?
    def flush(self):
        del self.commandstack
        self.commandstack = []

class InvalidTorrentCommandException(Exception):
    """
    Thrown on an invalid command.
    """

class AttributeDictMultiResult(dict):
    def __getattr__(self, attr):
        if attr in self:
            return self[attr]
        else:
            raise AttributeError('%s not in dict' % attr)

