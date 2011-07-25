"""

.. _rtorrentquery-class:

RTorrentQuery
=============

The RTorrent query class can be used to send multiple queries over one
XMLRPC command, thus heavily decreasing loading times.

It is created in RTorrent.query() or can be manually created using the
RTorrentQuery() constructor.

It extends the MultiBase class, which is used in all the *Query classes.
Head over to :ref:`multibase-class` to find more about the general *Query classes.

.. code-block:: python

    # Create a RTorrent class (or use an existing one)
    r = RTorrent(host, port, url)

    # Create the query.
    rq = r.query().get_upload_rate().get_download_rate(\
).get_librtorrent_version()

    res = rq.first()

    print res.get_upload_rate # Note that this is an attribute.
"""
from lib.multibase import MultiBase
from model import rtorrent

class RTorrentQuery(MultiBase):
    """
        The RTorrent query class can be used to send multiple queries over one
        XMLRPC command, thus heavily decreasing loading times.
    """

    def __init__(self, *args):
        """
        Pass the host, port, url and possible default arguments.
        """

        MultiBase.__init__(self, *args)
        self._rpc_methods = rtorrent._rpc_methods

