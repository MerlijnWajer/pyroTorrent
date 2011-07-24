.. pyroTorrent documentation master file, created by
   sphinx-quickstart on Sun Jan 23 16:32:39 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


Introduction to pyroTorrent
===========================

What is pyroTorrent?
--------------------

pyroTorrent is a web interface to rTorrent, the popular bittorrent client.
pyroTorrent was created to rid servers of that awful project called PHP. It is a
disgrace to programming languages in general. Anyway, enough ranting, as the
code of this project sucks too, just less than any PHP project. pyroTorrent is
still very much work in progress. It can only show some basic information about
torrents, list them and you can add torrents by passing the URL. The design
sucks. But it is quite fast. Faster than most rtorrent (did I mention it's for
rtorrent? Now I did.) web interfaces. 

Features
--------

It's features include but are not limited to:

    -   View your torrents and upload/download rate.
    -   Efficient XMLRPC usage.
    -   Browse the files of your torrents.
    -   Add torrents via direct links to .torrent files

Planned features:

    -   Implement direct SCGI communication.
    -   Support torrent views.
    -   Add events / schedulers.
    -   Encryption policy management.
    -   Support for transmission
    -   Add lots of statistics. (database, graphs?)

Download / Source code
----------------------

Git source code:

.. code-block:: bash

    git clone git://github.com/MerlijnWajer/pyroTorrent.git

PyroTorrent's documentation
===========================

.. toctree::
    :maxdepth: 2

    intro.rst
    rtorrent.rst
    torrent.rst
    baserequester.rst
    torrentrequester.rst
    multibase.rst
    torrentquery.rst
    rtorrentquery.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

