import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from pyrotorrent.lib.base import BaseController, render

from pyrotorrent.lib import app_globals
from pyrotorrent.lib.torrentrequester import TorrentRequester
from pyrotorrent.lib.filerequester import TorrentFileRequester

from pyrotorrent.model.torrent import Torrent
from pyrotorrent.model.rtorrent import RTorrent

log = logging.getLogger(__name__)

class TorrentinfoController(BaseController):

    def index(self, torrenthash):
        host, port, url = app_globals.rtorrent['host'], \
            app_globals.rtorrent['port'], app_globals.rtorrent['url']

        t = Torrent(torrenthash, **app_globals.rtorrent)

        q = t.query()

        q.get_name().get_size_bytes().get_bytes_left().get_loaded_file()

        c.t = q.all()[0]

        c.t.get_files = TorrentFileRequester(host, port, url,
                t._hash, '').get_path_components().all()

        r = RTorrent(host, port, url)

        rquery = r.query().get_upload_rate().get_download_rate(\
                ).get_libtorrent_version()
        c.r = rquery.first()

        return render('/torrentinfo.jinja2')
