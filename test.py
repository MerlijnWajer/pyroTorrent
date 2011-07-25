from model.rtorrent import RTorrent
import socket

r = RTorrent()

try:
    print 'libTorrent version:', r.get_libtorrent_version()
except socket.error, e:
    print 'Failed to connect to libTorrent:', str(e)
