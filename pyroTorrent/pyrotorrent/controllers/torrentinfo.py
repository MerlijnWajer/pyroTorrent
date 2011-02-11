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

        q = t.query()

        q.get_name().get_size_bytes().get_bytes_left().get_loaded_file()

        c.t = q.all()[0]
        c.t.get_files = t.get_files()

        return render('/torrentinfo.jinja2')
