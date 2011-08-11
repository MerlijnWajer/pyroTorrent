#!/usr/bin/env python
from model.torrent import Torrent
from model.rtorrent import RTorrent
from model.peer import Peer

from lib.torrentrequester import TorrentRequester
from lib.peerrequester import PeerRequester

from config import rtorrent_config
from lib.config_parser import parse_config_part, RTorrentConfigException

targets = []
for x in rtorrent_config:
    try:
        info = parse_config_part(rtorrent_config[x], x)
    except RTorrentConfigException, e:
        print 'Invalid config: ', e
        sys.exit(1)

    targets.append(info)

if len(x) == 0:
    print 'No targets'
    sys.exit(1)

r = RTorrent(targets[0])

print '''Welcome to the pyroTorrent CLI interface.
We have created a RTorrent() object called 'r'.

Use the help() commands to find out how to use the client interface;
help(RTorrent), help(Torrent) might be helpful'''

print 'RTorrent object using target: ', targets[0]
