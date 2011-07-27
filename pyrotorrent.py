#!/usr/bin/env python
"""
pyroTorrent module.
"""

from flup.server.fcgi import WSGIServer
from jinja2 import Environment, PackageLoader

from webtool import WebTool, read_post_data

import datetime
import time

# For unescaping
import urllib

# For torrent downloading
import urllib2

# Binary object encoding
import xmlrpclib

# Regex
import re

from beaker.middleware import SessionMiddleware

# Future: for JSON.
import simplejson as json

from config import *

from sessionhack import SessionHack, SessionHackException

from model.rtorrent import RTorrent
from model.torrent import Torrent

from lib.multibase import InvalidTorrentException, InvalidConnectionException

from lib.torrentrequester import TorrentRequester
from lib.filerequester import TorrentFileRequester
from lib.filetree import FileTree


def pyroTorrentApp(env, start_response):
    """
    pyroTorrent main function.
    """

    # Log here if you want

    r = wt.apply_rule(env['REQUEST_URI'], env)

    # 404
    if r is None:
        start_response('404 Not Found', [('Content-Type', 'text/html')])
        tmpl = jinjaenv.get_template('404.html')

        rtorrent_data = fetch_global_info()

        return template_render(tmpl, {
            'url' : env['REQUEST_URI'], 'session' : env['beaker.session'],
            'rtorrent_data' : rtorrent_data},
            default_page=False)

    elif type(r) in (tuple, list) and len(r) >= 1:
        # Respond with custom type.
        start_response('200 OK', [('Content-Type', r[0])])
        r = r[1]

    # 200
    else:
        start_response('200 OK', [('Content-Type', 'text/html;charset=utf8')])

    # Response data
    return [r]

def template_render(template, vars, default_page=True):
    """
        Template Render is a helper that initialisaes basic template variables
        and handles unicode encoding.
    """
    vars['base_url'] = BASE_URL
    vars['static_url'] = STATIC_URL

    return unicode(template.render(vars)).encode('utf8')

def fetch_global_info():
    """
    Fetch global stuff (always displayed):
        -   Down/Up Rate.
        -   IP (perhaps move to static global)
    """
    global global_rtorrent
    try:
        r = global_rtorrent.query().get_upload_rate().get_download_rate().get_ip()\
            .get_hostname().get_memory_usage().get_max_memory_usage()\
            .get_libtorrent_version()
        return r.first()
    except InvalidConnectionException, e:
        return {}

# These *_page functions are what you would call ``controllers''.
def main_page(env):

    try:
        t = TorrentRequester('')

        t.get_name().get_download_rate().get_upload_rate() \
                .is_complete().get_size_bytes().get_download_total().get_hash()

        torrents = t.all()

    except InvalidTorrentException, e:
        return error_page(env, str(e))

    rtorrent_data = fetch_global_info()

    tmpl = jinjaenv.get_template('download_list.html')

    return template_render(tmpl, {'session' : env['beaker.session'],
        'torrents' : torrents, 'rtorrent_data' : rtorrent_data} )

def error_page(env, error='No error?'):
    rtorrent_data = fetch_global_info()
    tmpl = jinjaenv.get_template('error.html')
    return template_render(tmpl, {'session' : env['beaker.session'],
        'error' : error,
        'rtorrent_data' : rtorrent_data })

def torrent_info_page(env, torrent_hash):
    try:
        t = Torrent(torrent_hash)
        q = t.query()
        q.get_name().get_size_bytes().get_download_total().get_loaded_file()\
                .get_message().is_active()
        torrentinfo = q.all()[0] # .first() ?

    except InvalidTorrentException, e:
        return error_page(env, str(e))

    # FIXME THIS IS UGLY

    files = TorrentFileRequester(t._hash, '')\
            .get_path_components().all()

    files = map(lambda x: x['get_path_components'], files)

    tree = FileTree(files).root

    rtorrent_data = fetch_global_info()

    tmpl = jinjaenv.get_template('torrent_info.html')

    return template_render(tmpl, {'session' : env['beaker.session'],
        'torrent' : torrentinfo, 'tree' : tree, 'rtorrent_data' : rtorrent_data} )

def torrent_action(env, torrent_hash, action):
    """
    Start, Stop, Pause, Resume, Delete torrent. I suppose. XXX TODO
    """
    # TODO: Implement Delete()
    try:
        t = Torrent(torrent_hash)
    except InvalidTorrentException, e:
        return error_page(env, str(e))

    # TODO: Check torrent status, return something like a JSON or Pickle result?
    # (Whether the stop/start/pause failed, etc)

    if action == 'start':
        t.start()
    elif action == 'stop':
        t.stop()
    elif action == 'pause':
        t.pause()
    elif action == 'resume':
        t.resume()
    else:
        raise Exception('Invalid torrent action')

    return 'lol'

def add_torrent_page(env):
    """
    Page for adding torrents.
    Works: Adding a correct torrent (URL only)
    What doesn't work:
        Error handling,
        Uploading .torrent files
        Option to add and start, or not start on add
    """

    return_code = None

    # Check for POST vars
    if str(env['REQUEST_METHOD']) == 'POST':
        data = read_post_data(env)
        if data is None:
            return str('Error: Invalid POST data')
        torrent_url = data['torrent_url'] if 'torrent_url' in data else None
        if torrent_url:
            torrent_url = urllib.unquote_plus(torrent_url)
            response = urllib2.urlopen(torrent_url)
            torrent_raw = response.read()

            torrent_raw_bin = xmlrpclib.Binary(torrent_raw)

            global global_rtorrent
            return_code = global_rtorrent.add_torrent_raw(torrent_raw_bin)

    rtorrent_data = fetch_global_info()

    tmpl = jinjaenv.get_template('torrent_add.html')

    if return_code == 0:
        torrent_added = 'SUCCES'
    elif return_code is not None:
        torrent_added = 'FAIL'
    else:
        torrent_added = ''

    return template_render(tmpl, {'session' : env['beaker.session'],
        'rtorrent_data' : rtorrent_data,
        'torrent_added': torrent_added} )


if __name__ == '__main__':
    jinjaenv = Environment(loader=PackageLoader('pyrotorrent', 'templates'))
    jinjaenv.autoescape = True
    wt = WebTool()

    # Add all rules
    execfile('rules.py')

    # Global helpers
    global_rtorrent = RTorrent()

    #WSGIServer(SessionMiddleware(pyroTorrentApp), \
    #        session_options).run()
    WSGIServer(SessionMiddleware(SessionHack(pyroTorrentApp, error_page), \
            session_options)).run()
