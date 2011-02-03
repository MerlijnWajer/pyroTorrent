"""
.. _multibase-class:

MultiBase
=========
"""

import xmlrpclib

class MultiBase(object):
    """
    MultiBase is a class that can be inherited to easily create a class that can
    send multiple XMLRPC commands in one request, using the xmlrpclib.MultiCall
    class. It also overrides several functions like __getattr__ and __call__ to
    make usage simple:

    .. code-block:: python

        t = Torrent.query() # Returns a TorrentQuery object which inherits from
                            # MultiBase
        t.get_name().get_hash()
        t.get_upload_rate()

        print t.all()
    """

    def __init__(self, host, port=80, url='/RPC2', *args):
        """
        """
        self.s = xmlrpclib.ServerProxy('http://%s:%i%s' % (host, port, url))
        self.m = xmlrpclib.MultiCall(self.s)

        self.host, self.port, self.url = host, port, url

        # Stack to put commands on
        self._groups = [[]]
        self._group_args = args

    def __call__(self, attr, *args):
        """
        Return self so we can chain calls.
        """
        _attr = self._convert_command(attr)

        total_args = list(self._group_args)
        total_args.extend(args)
        getattr(self.m, _attr)(*total_args)
        self._groups[-1].append(attr)

        return self

    def __getattr__(self, attr):
        """
        Used to add commands.
        """
        return lambda *args: self(attr, *args)

    def new_group(self, *args):
        """
        Use this to create a new group. You can chain calls as well.
        """
        self._groups.append([])
        self._group_args = args
        return self

    def all(self, model='', _type=AttributeDictMultiResult):
        """
        Returns a list of the results.
        _type can be 'list' or AttributeDictMultiResult.
        """
        if _type not in (AttributeDictMultiResult, list):
            raise InvalidTorrentCommandException('Invalid _type: %s' %
                    str(_type))

        xmlres = list(self.m())

        if _type is list:
            self._flush()
            return xmlres

        xmlres.reverse()

        result = []
        for group in self._groups:
            res = []
            for command in group:
                res.append(xmlres.pop())

            result.append(AttributeDictMultiResult(zip(group, res)))

        self._flush()

        return result

    def _flush(self):
        pass

    def _convert_command(self, command):
        """
        Convert command based on self._rpc_methods to rtorrent command.
        """
        if command in self._rpc_methods:
            return self._rpc_methods[command][0]
        else:
            raise InvalidTorrentCommandException("%s is not a valid command" %
                    command)

class InvalidTorrentCommandException(Exception):
    """
    Thrown on an invalid command.
    """

class AttributeDictMultiResult(dict):
    """
        AttributeDictMultiResult is basically just a dict object which also
        implements __getattr__ so you can access the dict values via .<name>.
    """
    def __getattr__(self, attr):
        if attr in self:
            return self[attr]
        else:
            raise AttributeError('%s not in dict' % attr)

