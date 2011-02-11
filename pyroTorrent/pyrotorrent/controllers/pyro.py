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
        host, port, url = app_globals.rtorrent['host'], \
            app_globals.rtorrent['port'], app_globals.rtorrent['url']
        r = RTorrent(host, port, url)

        t = TorrentRequester(host, port, url, '')

        t.get_name().get_download_rate().get_upload_rate() \
                .is_complete().get_size_bytes().get_download_total().get_hash()
        c.torrents = t.all()

        rquery = r.query().get_upload_rate().get_download_rate()

        c.r = rquery.first()

        return render('/download_list.jinja2')
