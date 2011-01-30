import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from pyrotorrent.lib.base import BaseController, render

from pyrotorrent.lib import app_globals
from pyrotorrent.lib.torrentrequester import TorrentRequester

from pyrotorrent.model.torrent import Torrent

log = logging.getLogger(__name__)

class TorrentinfoController(BaseController):

    def index(self, torrenthash):

        t = Torrent(torrenthash, **app_globals.rtorrent)
        c.t = t

        return render('/torrentinfo.jinja2')
