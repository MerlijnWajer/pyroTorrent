#!/usr/bin/env python
from model.torrent import Torrent
from model.rtorrent import RTorrent

from lib.torrentrequester import TorrentRequester

if __name__ == '__main__':
    r = RTorrent()
    print r.get_upload_rate()

    #torrents = r.get_download_list('')
    torrents = TorrentRequester('')
    torrents.get_hash().get_name()

    a = torrents.all()
    print a

    torrenthash = a[0].get_hash

    t = Torrent(torrenthash)

    q = t.query()

    q.get_name().get_size_bytes().get_bytes_left().get_loaded_file()

    print q.all()[0]
