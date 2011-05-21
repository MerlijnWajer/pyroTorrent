#!/usr/bin/env python
from pyrotorrent.model.torrent import Torrent
from pyrotorrent.model.rtorrent import RTorrent

from pyrotorrent.lib.torrentrequester import TorrentRequester

if __name__ == '__main__':
    r = RTorrent('sheeva')
    print r.get_upload_rate()
    
    #torrents = r.get_download_list('')
    torrents = TorrentRequester(r.host, r.port, r.url)
    torrents.get_hash().get_name()
    print torrents.all()
