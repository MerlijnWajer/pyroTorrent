import sys
sys.path.insert(0, '..')

import model.rtorrent as rtorrent
import model.torrent as torrent
import model.peer as peer


for d in (rtorrent, torrent, peer):
    for x, y in d._rpc_methods.iteritems():
        print y[0], y[1]
        #print y[0], '\n', y[1]
