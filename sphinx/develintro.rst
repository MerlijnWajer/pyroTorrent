Introduction for Developers
===========================

This page presents an introduction to the pyroTorrent design goals.

Understanding pyroTorrent
-------------------------

pyroTorrent's codebase might look complex at first, but it's ultimitely trivial
once you understand *why* we made certain design decisions. (Let's hope they
turn out to be right ones, it seems like they are so far).

The easiest way to help you understand our design decisions, is to simply share
our experiences and thoughts when we were planning to write pyroTorrent.

Since I currently suck as a writer, don't worry if you at some point don't
understand what I'm trying to say, just keep on reading. It will probably make
sense after you've read the entire page. If not, read it again. If you still
don't get it, it's either a case of PEBCAK or I just really suck at writing. :-)

Code design goal
----------------

After trying several rTorrent web frontends such as `wTorrent
<https://code.google.com/p/wtorrent-project/>`_ and `rTWi
<http://rtwi.jmk.hu/>`_, we were rather disappointed by the speed offered by
both these frontends, aside from the fact that they used PHP. (Which may be one
of the reasons they were so unresponsive)

Here's a very flawed and probably unfair comparison, with PHP admittedly compiled with -O1 (because
-O2 broke compilation...)

Loading the main/overview page with about ~150 torrents in queue:

==================== ============ =============
  pyroTorrent           rTWi      wTorrent
==================== ============ =============
 ~400 milli seconds   10+ seconds  8 seconds
==================== ============ =============

All tests are done on a Sheevaplug with 1,2 Ghz ARM processor, softfloat.

One of pyroTorrent's design goals is to be fast. One of the ways to achieve this
is to minimise the amount of XMLRPC calls with so called *multicalls*.

Multicalls
----------

``libTorrent`` and the Python module ``xmlrpclib`` both have support for a so
called *multicall*. A multicall in xmlrpclib typically encapsulates several
XMLRPC requests in one request, thus decreasing overhead a lot.
libTorrent multicalls perform an action on all items of a specific type, say
all torrents - simply with the call ``d.multicall``.
If you don't use multicall you'll rapidly find yourself opening over 500
connections per page load; and since XMLRPC is stateless you'll have to actually
do 500 requests, each with their own connection.

pyroTorrent makes use of both these multicall mechanisms. Typically it should
not open more than a few connections per page load. Current in release 0.04,
pyroTorrent does *only 2* XMLRPC requests to load the main overview page.


xmlrpclib Multicall
~~~~~~~~~~~~~~~~~~~

Below is some code from pyroTorrent release-0.03.

Fetching some rTorrent information:

.. code-block:: python

    try:
        r = global_rtorrent.query().get_upload_rate().get_download_rate().get_ip()\
            .get_hostname().get_memory_usage().get_max_memory_usage()\
            .get_libtorrent_version()
        return r.first()
    except InvalidConnectionException, e:
        return {}

As illustrated in an interactive python shell using pyroTorrent's ``cli.sh``:

>>> r.query().get_upload_rate().get_download_rate().get_ip()\
...         .get_hostname().get_memory_usage().get_max_memory_usage()\
...         .get_libtorrent_version().first()
{'get_memory_usage': 30408704, 'get_ip': '0.0.0.0', 'get_upload_rate': 16303,
'get_max_memory_usage': 858993459, 'get_hostname': 'sheeva',
'get_download_rate': 4932, 'get_libtorrent_version': '0.12.6'}

And all this information is retrieved in one XMLRPC call.

Note how we call ``.query()`` on the object ``r``. ``r`` is a :ref:`rtorrent`
instance; and the ``.query()`` method returns a :ref:`rtorrentquery` object.
The :ref:`rtorrentquery` object contains all the libTorrent calls that the
rtorrent object supports, but it remembers what calls you've done on the object,
and then returns them all when you tell it to. (The ``.first()`` call).
Also note how the :ref:`rtorrentquery` object allows you to chain calls, by
returning itself.

The :ref:`rtorrentquery` inherits from on the :ref:`multibase` class, which
takes care of all the underlying tasks. You'll find that :ref:`rtorrentquery`
is no more than 40 lines of code, of which 80% is documentation.

Apart from :ref:`rtorrentquery`, we also have :ref:`torrentquery`, which does
the same, but for the :ref:`torrent` model instead of the :ref:`rtorrent` model.


libTorrent Multicall
~~~~~~~~~~~~~~~~~~~~

Getting certain information of all torrents:

.. code-block:: python

    try:
        t = TorrentRequester('')

        t.get_name().get_download_rate().get_upload_rate() \
                .is_complete().get_size_bytes().get_download_total().get_hash()

        torrents = t.all()

    except InvalidTorrentException, e:
        return error_page(env, str(e))

Basic example in ``cli.sh``:

>>> t = TorrentRequester('')
>>> t.get_name().get_download_rate().get_upload_rate() \
... .is_complete().get_size_bytes().get_download_total().get_hash()
<lib.torrentrequester.TorrentRequester object at 0x24ae350>
>>> torrents = t.all()
>>> len(torrents)
83
>>> torrents[:1]
[{'get_size_bytes': 41907644, 'get_upload_rate': 0, 'get_name':
'RevengeOfTheTitansSoundtrack.zip', 'get_hash':
'6709A6306E2FB4EEF89455DFC8C26CA4DB316E6F', 'get_download_total': 0,
'get_download_rate': 0, 'is_complete': 0}]

The :ref:`torrentrequester` works somewhat similar to :ref:`rtorrentquery` in
the sense that it also uses multicalls; but in this case the libTorrent
multicall. The TorrentRequester inherits most of its functionality from
the :ref:`baserequester`.

pyroTorrent Model API
---------------------

libTorrent offers an API to program most if not all tasks; but the API is rather
undocumented and awkward to be used without any wrapper or model.

It would however become increasingly cumbersome to write a method for *each*
libTorrent method, so we've come up with a solution.

In the file ``model/rtorrent.py`` all the RPC methods are stored in a dict:

.. code-block:: python

    _rpc_methods = {
        'get_upload_throttle' : ('get_upload_rate',
            """
            Returns the current upload throttle.
            """),
        'set_upload_throttle' : ('set_upload_rate',
            """
            Set the upload throttle.
            Pass the new throttle size in bytes.
            """),
        'get_ip' : ('get_ip',
            """
            Returns the IP rtorrent is bound to. (For XMLRPC?)
            """)
    }

For each entry in the dictionary, a method is generated and added to the
:ref:`rtorrent` class, along with a ``__doc__`` entry:

.. code-block:: python

    for x, y in _rpc_methods.iteritems():
        caller = (lambda name: lambda self, *args: getattr(self.s, name)(*args))(y[0])
        caller.__doc__ = y[1] + '\nOriginal libTorrent method: ``%s``' % y[0]
        setattr(RTorrent, x, types.MethodType(caller, None, RTorrent))
    
        del caller

.. GETRIDOFVIMHIGHLIGHTBUG*

We do something similar for the :ref:`torrent` class.


