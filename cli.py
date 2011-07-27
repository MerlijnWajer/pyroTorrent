#!/usr/bin/env python
from model.torrent import Torrent
from model.rtorrent import RTorrent

from lib.torrentrequester import TorrentRequester

r = RTorrent()

print '''Welcome to the pyroTorrent CLI interface.
We have created a RTorrent() object called 'r'.

Use the help() commands to find out how to use the client interface;
help(RTorrent), help(Torrent) might be helpful'''
