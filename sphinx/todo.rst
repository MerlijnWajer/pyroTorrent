.. _TODO:

TODO
====

This page will contain a small list of things that have to be done; although
it'll probably mainly serve as a braindump page on TODO items. (We already have
a list of things to do in the TODO file)

List:
    
    -   Figure out what each model should do. It may help to look at the
        RTorrent XMLRPC commands. [1]
        Is a download the same as a torrent? And what is a *File* (in the
        RTorrent commands list)

        [1] http://libtorrent.rakshasa.no/wiki/RTorrentCommands

    -   Create some simple models. (RTorrent, Torrent). (Including XMLRPC)
        Doesn't have to include all the functionality rtorrent offers.

        We have to decide on how we are going to use xmlrpclib in the models.
        The easiest way would be to pass a host, port and url to each model. (Or
        perhaps a xmlrpclib.ServerProxy object? Since every model will have to
        do it's own look ups, they'll all need a host+port+url.

        We'll also have to think about error handling.

    -   Some basic web interface. (Perhaps a login + list torrents by view?)
