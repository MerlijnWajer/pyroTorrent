from model.rtorrent import RTorrent
import socket

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

for x in targets:
    r = RTorrent(x)

    try:
        print '[', x['name'], '] libTorrent version:', r.get_libtorrent_version()
    except socket.error, e:
        print 'Failed to connect to libTorrent:', str(e)
