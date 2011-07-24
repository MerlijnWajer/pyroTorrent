.. _introduction:

Introduction to pyroTorrent
===========================

What is pyroTorrent?
--------------------

pyroTorrent is a web interface to rTorrent, the popular bittorrent client.

Features
--------


It's features include but are not limited to:

    -   View your torrents and upload/download.
    -   Efficient XMLRPC usage.
    -   Browse the files of your torrents.

Planned features:

    -   Add torrents via direct links to .torrent files
    -   Support torrent views.
    -   Add lots of statistics. (database, graphs?)
    -   Add events / schedulers.
    -   Encryption policy management.
    -   Support for transmission

Setting up pyroTorrent
======================

Requirements
------------

pyroTorrent is written in Python. Aside from Python, you'll need the following
python packages:

    -   jinja2
    -   flup (WSGIServer)
    -   beaker
    -   simplejson (not yet but will soon)

as well as rtorrent with XMLRPC support. pyroTorrent has only been tested on
GNU/Linux, so this would be an advantage as well.

.. TERRIBLE NAME vvvvvv

Deciding on your setup
----------------------

Currently the only supported way of setting up pyroTorrent is to have
rtorrent expose a XMLRPC interface over a HTTPD (in our case, we used
`lighttpd <http://www.lighttpd.net/>`_. pyroTorrent will *talk* to rtorrent via
the HTTPD, and it will also make use of (possibly another) HTTPD to expose its
web interface.

Throughout the entire setup manual we will make the following assumptions:

    -   You know your way around the terminal - at least a bit.
    -   You are smart enough to adjust out exemplary paths to your own.

Our setup is as follows: (Compare it to your own, or how you will be wanting to
set it up)

    -   The *user* ``rtorrent`` runs ``rtorrent``. 
    -   The *user* ``rtorrent`` has a folder called ``pyrotorrent`` in it's home
        directory, (*/home/rtorrent*) this is the directory containing th
        pyroTorrent source code.
    -   The HTTPD users and groups are *lighttpd* (at least in the lighttpd
        example)
    -   You know how to configure your HTTPD (lighttpd in our case); your
        webroot directory is assumed to be */var/www*. It doesn't matter to
        pyroTorrent but the examples use this directory.

AT ALL TIMES make sure you use the appropriate paths.

rTorrent configuration
----------------------

In your *.rtorrent.rc* file, you need at least this line:

.. code-block:: bash

    scgi_local = /home/rtorrent/rtorrentsock/rpc.socket

Where */home/rtorrent/rtorrentsock/rpc.socket* is the path to the socket file
rtorrent will create for communication with the HTTPD. You'll also need to make
sure the socket is writeable by rtorrent as well as the HTTPD.

Having this option in your *.rtorrent.rc* is also recommended:

.. code-block:: bash

    encoding_list = UTF-8

although at the moment I do not recall why it was required.

.. TODO LOL XXX FIXME ^^^

Restart rtorrent once you've changed the configuration, if the socket file is
created then you've set up your *.rtorrent.rc* correctly. Now, don't forget to
make it writable by the web server as well.

Webserver configuration
-----------------------

Now that we've got the rtorrent side working, let's have a look at the HTTPD
side.

Lighttpd
~~~~~~~~

Lighttpd is known to work well with pyroTorrent.

Setting up SCGI
```````````````

We need ``mod_scgi`` for the rtorrent <-> HTTPD connection.

We need to include ``mod_scgi``, so put this in your configuration file:

.. code-block:: lua

    server.modules += ("mod_scgi")

Add this to your configuration file:

.. code-block:: lua

        scgi.server = (
          "/RPC2" =>
                ( "127.0.0.1" =>
                  (
                  "socket" => "/home/rtorrent/rtorrentsock/rpc.socket",
                  "disable-time" => 0,
                  "check-local" => "disable"
                  )
                )
        )

Again, make notice of the path */home/rtorrent/rtorrentsock/rpc.socket* that you
set in `rTorrent configuration`_.

Testing SCGI
````````````

Now we can test your SCGI setup. Don't forget to restart lighttpd to make sure
the configuration changes have been loaded.
Now, pyroTorrent offers a little test file called ``test.py``:

.. code-block:: python

    from model.rtorrent import RTorrent
    import socket

    r = RTorrent()

    try:
        print 'libTorrent version:', r.get_libtorrent_version()
    except socket.error, e:
        print 'Failed to connect to libTorrent:', str(e)

Which should return your rTorrent version on success, and otherwise will tell
you what went wrong. However, we cannot yet test our connection with pyroTorrent
since we did not yet create a basic pyroTorrent configuration file.
See `Basic pyroTorrent configuration`_ on how to do this.

Once you've done this, verify that pyroTorrent works:

.. code-block:: bash

    $ python test.py
    libTorrent version: 0.12.6

Setting up FCGI
```````````````

We need to include ``mod_fastcgi``, so put this in your configuration file:

.. code-block:: lua

    server.modules += ("mod_fastcgi")

Somewhere on top, but below the *server.modules =* line, (or just add it to your
standard set of modules). In some cases a mod_fastcgi.conf file is shipped with
your distribution instead. You can use this file by including it, but make sure
it doesn't do any weird stuff like set up PHP. (Who would want that anyway?)

.. code-block:: lua

    include "mod_fastcgi.conf"

There. Now we should have fastcgi support for lighttpd. If this went too fast,
have a look at the lighttpd documentation.

Setting up FCGI to talk to pyroTorrent
``````````````````````````````````````

This is the tricky part. You'll need to ensure that a couple of things work:

    -   An empty file is required in your document root to prevent 404's before
        the FCGI contact is made.
    -   You have the appropriate *rewrite-once* rule.
    -   You have an *alias.url* for the static files.
    -   You have the correct *fastcgi.server* line.

.. code-block:: lua

    url.rewrite-once = (
             "^/torrent" => "torrent.tfcgi"
    )

    fastcgi.server += ( ".tfcgi" =>
       ( "torrentfcgi" =>
         (
             "socket"        => "/tmp/torrent.sock-1",
             "docroot"       => "/home/rtorrent/pyrotorrent"
         )
       )
     )
    alias.url += ("/static/torrent/" => "/home/rtorrent/pyrotorrent/static/")

And don't forget to create the empty file:

.. code-block:: lua

    touch /var/www/torrent.tfcgi

Where */var/www* is my *var.basedir* in the lighttpd configuration file.

Using spawn-fcgi
````````````````

To spawn an instance of pyroTorrent, we use the program called *spawn-fcgi*.
It's probably in your package manager; install it. Run the following command as
root, obviously again adjust whatever parameters you need to adjust.

.. code-block:: bash

    /usr/bin/spawn-fcgi /home/rtorrent/pyrotorrent/pyrotorrent.py \
    -s /tmp/torrent.sock-1 \
    -u lighttpd -g lighttpd \
    -d /home/rtorrent/pyrotorrent/

Where the socket path is defined by *-s*, the user and group of the pid
are set with *-u* and *-g*, and finally, the directory to change to is
defined by *-d*.

Now that you've spawned a pyroTorrent process, let's check that it's still
alive:

.. code-block:: bash

    # ps xua  |grep python
    lighttpd 31639 84.5  1.6  12276  8372 ?        Rs   19:57   0:01    /usr/bin/python2.6 /home/rtorrent/pyrotorrent/pyrotorrent.py

Apache
~~~~~~

TODO.

Nginx
~~~~~

TODO.

pyroTorrent configuration
-------------------------


The pyroTorrent configuration file is trivial.

Basic pyroTorrent configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A basic configuration file (just enough for the famous ``test.py``) looks like
this:

.. code-block:: python

    rtorrent_config = {
            'host' : '192.168.1.70', # IP where your HTTPD+rtorrent resides.
            'port' : 80, # HTTPD port
            'url'  : '', # URL can typically be empty.
        }


To actually serve webpages over FCGI, we need to extend the configuration file a
bit:

.. code-block:: python

    # Place all your globals here

    # ``Base'' URL for your HTTP website
    BASE_URL = '/torrent'
    # HTTP URL for the static files
    STATIC_URL = '/static/torrent'

    rtorrent_config = {
            'host' : '192.168.1.70', # IP where your HTTPD+rtorrent resides.
            'port' : 80, # HTTPD port
            'url'  : '', # URL can typically be empty.
        }

    session_options = {
        'session.cookie_expires' : True
    }

