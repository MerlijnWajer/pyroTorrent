.. pyroTorrent documentation master file, created by
   sphinx-quickstart on Sun Jan 23 16:32:39 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


Introduction to πϱTorrent
===========================

.. figure:: pyrotorrent.png
    :scale: 25%

    A picture is worth a thousand words.

What is πϱTorrent?
------------------

πϱTorrent is a web interface to rTorrent, the popular bittorrent client.
πϱTorrent was created to rid servers of that awful project called PHP. It is a
disgrace to programming languages in general. Anyway, enough ranting, as the
code of this project sucks too, just less than any PHP project. pyroTorrent is
still very much work in progress. It can only show some basic information about
torrents, list them and you can add torrents by passing the URL. The design
sucks. But it is quite fast. Faster than most rtorrent (did I mention it's for
rtorrent? Now I did.) web interfaces.

Features
--------

Its features include but are not limited to:

    -   View your torrents and upload/download rate.
    -   Efficient XMLRPC usage.
    -   Browse the files of your torrents.
    -   Add torrents via direct links to .torrent files
    -   Basic support for rtorrent views.
    -   Direct SCGI communication over Unix sockets as well as HTTP XMLRPC.
    -   Multiple rtorrent sources. (``targets``)
    -   Support for basic user management. (config file + per target)
    -   Download (in)complete files using your browser.
    -   Support for resuming aforementioned downloads. (HTTP 206)

Planned features:

    -   Select/Change/Create/Delete views
    -   Advanced user management.
    -   Add events / schedulers.
    -   Encryption policy management.
    -   Manage lots of rtorrent settings.
    -   Move torrents to views
    -   Add statistics. (graphs)
    -   And a lot more...

Far fetched:

    -   Support for transmission
    -   Support for other clients. (uTorrent, Azureus)

Additionally, pyroTorrent tries to document most of the rTorrent XMLRPC methods
it uses. Its documentation of the rTorrent XMLRPC methods is probably far more
complete than rTorrent's own documentation. We hope to send our documentation to
the rTorrent project at some point and make the world a less chaotic place.

Download / Source code
----------------------

Git source code:

.. code-block:: bash

    git clone git://github.com/MerlijnWajer/pyroTorrent.git

Web view (mirror) https://git.wizzup.org/pyroTorrent.git/.

πϱTorrent's documentation
=========================

.. toctree::
    :maxdepth: 2

    setup.rst
    develintro.rst
    rtorrent.rst
    torrent.rst
    peer.rst
    baserequester.rst
    torrentrequester.rst
    peerrequester.rst
    multibase.rst
    torrentquery.rst
    rtorrentquery.rst
    decorator.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

