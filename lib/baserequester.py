"""
.. _baserequester-class:

BaseRequester
=============

BaseRequester is a class created to provide an easy way to create classes that
implement a lot of operations over XMLRPC. It is not the same as
:ref:`multibase-class` in the sense that this performs operations on all the
items in the view. (For example, :ref:`torrentrequester-class` implements a
method to get the name of each torrent in a view by simply calling .get_name().
"""

from lib.xmlrpc import RTorrentXMLRPC
from lib.multibase import InvalidTorrentCommandException


class BaseRequester(object):
    """
    """

    def __init__(self, target):
        """
        """
        self.s = RTorrentXMLRPC(target)

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
        except AttributeError, e:
            raise InvalidTorrentCommandException(e.message)
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
        return res


    def all(self):
        """
        Returns a list of the results.
        """
        _res = self._fetch()
        self.__res = [DictAttribute(zip(self.commandistack, x)) for x in _res]
        return self.__res

    def as_list(self):
        """
        """
        _res = self._fetch()
        return _res

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

class DictAttribute(dict):
    def __getattr__(self, attr):
        if attr in self:
            return self[attr]
        else:
            raise AttributeError('%s not in dict' % attr)

