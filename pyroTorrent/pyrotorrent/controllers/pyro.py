import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from pyrotorrent.lib.base import BaseController, render

# XXX: THIS OK?
from pyrotorrent.lib import app_globals
from pyrotorrent.lib.torrentrequester import TorrentRequester

from pyrotorrent.model.rtorrent import RTorrent
from pyrotorrent.model.torrent import Torrent

log = logging.getLogger(__name__)

class PyroController(BaseController):

    def index(self):
        r = RTorrent(**app_globals.rtorrent)

        t = TorrentRequester(**app_globals.rtorrent)
        t.get_name()
        c.torrents = t.all()

        return render('/download_list.jinja2')
