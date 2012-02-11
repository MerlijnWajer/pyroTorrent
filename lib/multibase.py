"""
.. _multibase-class:

MultiBase
=========

MultiBase is a class that can be inherited to easily create a class that can
send multiple XMLRPC commands in one request, using the xmlrpclib.MultiCall
class. RTorrentQuery and TorrentQuery implement this class.

It also overrides several functions like __getattr__ and __call__ to
make usage simple:

.. code-block:: python

    t = Torrent.query() # Returns a TorrentQuery object which inherits from
                        # MultiBase
    t.get_name().get_hash()
    t.get_upload_rate()

    print t.all()
"""

import xmlrpclib
import socket

from lib.xmlrpc import RTorrentXMLRPC

class MultiBase(object):
    """
    """
    def __init__(self, target, *args):
        """
        """
        self.s = RTorrentXMLRPC(target)
        self.m = xmlrpclib.MultiCall(self.s)

        # Stack to put commands on
        self._groups = [[]]

        # We keep these purely for hash functionality
        self._groups_args = [[]]
        self._def_group_args = args

    def __hash__(self):
        h = 42
        for y in zip(self._groups, self._groups_args):
            for x in zip(y[0], y[1]):
                h ^= hash(x[0])
                for z in x[1]:
                    h ^= hash(z)

        return h

    def __call__(self, attr, *args):
        """
        Add the attribute ``attr'' to the list we want to fetch.

        Return self so we can chain calls.
        """
        _attr = self._convert_command(attr)

        total_args = list(self._def_group_args)
        total_args.extend(args)
        getattr(self.m, _attr)(*total_args)
        self._groups[-1].append(attr)
        self._groups_args[-1].append(total_args)

        return self

    def __getattr__(self, attr):
        """
        Used to add commands.
        """
        return lambda *args: self(attr, *args) # calls __call__

    def new_group(self, *args):
        """
        Use this to create a new group. You can chain calls as well.
        """
        self._groups.append([])
        self._groups_args.append([])
        self._def_group_args = args
        return self

    def all(self, _type=None):
        """
        Returns a list of the results.

        _type can be 'list' or AttributeDictMultiResult.
        """
        if _type is None:
            _type = AttributeDictMultiResult
        if _type not in (AttributeDictMultiResult, list):
            raise InvalidTorrentCommandException('Invalid _type: %s' %
                    str(_type))

        try:
            xmlres = list(self.m())
        except xmlrpclib.Fault, e:
            raise InvalidTorrentException(e)
        except socket.error, s:
            raise InvalidConnectionException(s)

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

    def first(self, _type=None):
        """
        Return the first result.
        """
        res = self.all(_type)
        if len(res):
            return res[0]
        else:
            return None

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

class InvalidTorrentException(Exception):
    """
    Thrown on xmlrpc error.
    """

class InvalidConnectionException(Exception):
    """
    Thrown on xmlrpc error.
    """

class AttributeDictMultiResult(dict):
    """
        AttributeDictMultiResult is used by MultiBase .all() calls to return
        data in a somewhat usable manner. It's basically a dict with an extra
        feature to access the dict values via .<name> instead of [name].
    """
    def __getattr__(self, attr):
        if attr in self:
            return self[attr]
        else:
            raise AttributeError('%s not in dict' % attr)

