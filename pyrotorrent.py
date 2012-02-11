"""
TODO:
    -   Default arguments for jinja (wn, etc)
    -   Login decorators, etc.
    -   torrent_get_file
    -   torrent_file
    -   add_torrent_page
    -   torrent_info_page

"""


from flask import Flask, request, session, g, redirect, url_for, \
             abort, render_template, flash

from flask import Response

# TODO http://flask.pocoo.org/docs/config/

SECRET_KEY = 'development key'
DEBUG = True
USERNAME = 'admin'
PASSWORD = 'default'

app = Flask(__name__)
app.config.from_object(__name__)


from config import FILE_BLOCK_SIZE, BACKGROUND_IMAGE, \
        USE_AUTH, ENABLE_API, rtorrent_config, torrent_users

from lib.config_parser import parse_config_part, parse_user_part, \
    RTorrentConfigException, CONNECTION_SCGI, CONNECTION_HTTP

from model.rtorrent import RTorrent
from model.torrent import Torrent

from lib.multibase import InvalidTorrentException, InvalidConnectionException, \
    InvalidTorrentCommandException

from lib.torrentrequester import TorrentRequester
from lib.filerequester import TorrentFileRequester
from lib.filetree import FileTree

# TODO REMOVE?
from lib.helper import wiz_normalise, template_render, error_page, loggedin, \
    loggedin_and_require, parse_config, parse_users, fetch_user, \
    fetch_global_info, lookup_user, lookup_target, redirect_client_prg, \
    redirect_client
from lib.decorator import webtool_callback, require_torrent, \
    require_rtorrent, require_target

# For MIME
import mimetypes

# For stat and path services
import os
import stat

import datetime
import time

@app.route('/')
@app.route('/view/<view>')
def main_view_page(view='default'):
    """
    TODO: Login
    """

    rtorrent_data = fetch_global_info()

    user = None
#    user = fetch_user(env)

#    if view not in rtorrent_data.get_view_list:
#        return error_page(env, 'Invalid view: %s' % view)

    torrents = {}
    for target in targets:
        if user == None and USE_AUTH:
            continue
        if user and (target['name'] not in user.targets):
            continue

        try:
            t = TorrentRequester(target, view)

            t.get_name().get_download_rate().get_upload_rate() \
                    .is_complete().get_size_bytes().get_download_total().get_hash()

            h = hash(t)

            torrents[target['name']] = cache.get(h)
            if torrents[target['name']]:
                continue

            torrents[target['name']] = cache.get(target['name'])
            if torrents[target['name']] is not None:
                continue

            torrents[target['name']] = t.all()

            cache.set(h, torrents[target['name']], timeout=10)

        except InvalidTorrentException, e:
            return error_page(env, str(e))

    return render_template('download_list.html',
            torrents_list=torrents, rtorrent_data=rtorrent_data, view=view
            # TODO
            ,wn=wiz_normalise
            )

@app.route('/target/<target>/torrent/<torrent_hash>')
def torrent_info_page(target, torrent_hash):
    # TODO UNSAFE NEEDS DECORATOR
    target = lookup_target(target)
    torrent = Torrent(target, torrent_hash)

    try:
        q = torrent.query()
        q.get_hash().get_name().get_size_bytes().get_download_total().\
                get_loaded_file().get_message().is_active()
        torrentinfo = q.all()[0] # .first() ?

    except InvalidTorrentException, e:
        return error_page(env, str(e))

    files = TorrentFileRequester(target, torrent._hash)\
            .get_path_components().get_size_chunks().get_completed_chunks()\
            .all()

    tree = FileTree(files).root

    rtorrent_data = fetch_global_info()

    return render_template('torrent_info.html', torrent=torrentinfo, tree=tree,
        rtorrent_data=rtorrent_data, target=target,
        file_downloads=target.has_key('storage_mode')

        # TODO FIX ME
        ,wn=wiz_normalise
    )

@app.route('/target/<target>/torrent/<torrent_hash>.torrent')
def torrent_file(target, torrent_hash):
    pass

@app.route('/target/<target>/torrent/<torrent_hash>/get_file/<filename>')
def torrent_get_file(target, torrent_hash, filename):
    pass

@app.route('/target/<target>/add_torrent')
def add_torrent_page(target):
    pass

#wt.add_rule(re.compile('^%s/style.css$' % BASE_URL), style_serve, [])
#
#wt.add_rule(re.compile('^%s/login' % BASE_URL), handle_login, [])
#
#wt.add_rule(re.compile('^%s/logout' % BASE_URL), handle_logout, [])

@app.route('/api')
def api():
    pass

@app.route('/style.css')
def style_serve():
    """
    TODO: Re-add user lookup and user specific image:

    if user and user.background_image != None:
        background = user.background_image

    """
    background = BACKGROUND_IMAGE

    return Response(render_template('style.css',
        background_image=background,
        trans=0.6),
        mimetype='text/css',)


#if ENABLE_API:
#    wt.add_rule(re.compile('^%s/api' % BASE_URL), handle_api, [])

if __name__ == '__main__':
    targets = parse_config()
    users = parse_users()

    from werkzeug.contrib.cache import SimpleCache
    cache = SimpleCache()

    import lib.helper
    lib.helper.targets = targets
    lib.helper.users = users
    lib.helper.cache = cache

    app.run()
