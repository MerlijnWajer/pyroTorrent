#!/usr/bin/env python
"""
pyroTorrent module.
"""

from jinja2 import Environment, PackageLoader

from lib.webtool import WebTool, read_post_data

import datetime
import time

# For unescaping
import urllib

# For torrent downloading
import urllib2

# Binary object encoding
import xmlrpclib

# base64 dec+enc
import base64

# Regex
import re

from beaker.middleware import SessionMiddleware

# Future: for JSON.
import simplejson as json

# For sys.exit(), etc
import sys

from config import BASE_URL, STATIC_URL, BACKGROUND_IMAGE, USE_AUTH, \
    rtorrent_config, torrent_users
try:
    from config import USE_OWN_HTTPD
except ImportError:
    USE_OWN_HTTPD = False # sane default?

from lib.config_parser import parse_config_part, parse_user_part, \
    RTorrentConfigException, CONNECTION_SCGI, CONNECTION_HTTP

from lib.sessionhack import SessionHack, SessionHackException
from lib.login import verify_target

from model.rtorrent import RTorrent
from model.torrent import Torrent

from lib.multibase import InvalidTorrentException, InvalidConnectionException

from lib.torrentrequester import TorrentRequester
from lib.filerequester import TorrentFileRequester
from lib.filetree import FileTree

# For MIME
import mimetypes

# Main app
def pyroTorrentApp(env, start_response):
    """
    pyroTorrent main function.
    """
    # Log here if you want

    r = wt.apply_rule(env['PATH_INFO'], env)

    # 404
    if r is None:
        start_response('404 Not Found', [('Content-Type', 'text/html')])
        tmpl = jinjaenv.get_template('404.html')

        rtorrent_data = fetch_global_info()

        return template_render(tmpl, env,
            {'url' : env['PATH_INFO'],
            'rtorrent_data' : rtorrent_data})

    elif type(r) in (tuple, list) and len(r) >= 1:
        # Respond with custom type.
        start_response('200 OK', [('Content-Type', r[0])])
        r = r[1]

    # 200
    else:
        start_response('200 OK', [('Content-Type', 'text/html;charset=utf8')])

    # Response data
    return [r]

# Pulled somewhere from the net. Used in jinja.
def wiz_normalise(a):
    a = float(a)
    if a >= 1099511627776:
        terabytes = a / 1099511627776
        size = '%.2fT' % terabytes
    elif a >= 1073741824:
        gigabytes = a / 1073741824
        size = '%.2fG' % gigabytes
    elif a >= 1048576:
        megabytes = a / 1048576
        size = '%.2fM' % megabytes
    elif a >= 1024:
        kilobytes = a / 1024
        size = '%.2fK' % kilobytes
    else:
        size = '%.2fb' % a
    return size

def lookup_target(name):
    """
    Simple helper to find the target with the name ``name``.
    """

    for x in targets:
        if x['name'] == name:
            return x
    return None

def lookup_user(name):
    """
    """

    for x in users:
        if x.name == name:
            return x
    return None

def loggedin(env):
   return 'user_name' in env['beaker.session']

def loggedin_and_require(env):
    if USE_AUTH:
        return loggedin(env)
    else:
        return True

# Function to render the jinja template and pass some simple vars / functions.
def template_render(template, env, vars):
    """
        Template Render is a helper that initialises basic template variables
        and handles unicode encoding.
    """
    vars['base_url'] = BASE_URL
    vars['static_url'] = STATIC_URL
    vars['use_auth'] = USE_AUTH
    vars['wn'] = wiz_normalise
    vars['login'] = env['beaker.session']['user_name'] if \
        env['beaker.session'].has_key('user_name') else None

    ret = unicode(template.render(vars)).encode('utf8')

    return ret

# Fetch some useful rtorrent info from all targets.
def fetch_global_info():
    """
    Fetch global stuff (always displayed):
        -   Down/Up Rate.
        -   IP (perhaps move to static global)
    """
    res = {}
    for target in targets:
        rtorrent = RTorrent(target)
        try:
            r = rtorrent.query().get_upload_rate().get_download_rate()\
                .get_upload_throttle().get_download_throttle().get_ip()\
                .get_hostname().get_memory_usage().get_max_memory_usage()\
                .get_libtorrent_version().get_view_list()
            res[target['name']] = r.first()
        except InvalidConnectionException, e:
            print 'InvalidConnectionException:', e
            # Do we want to return or just not get data for this target?
            # I'd say return for now.
            return {}

    return res

# These *_page functions are what you would call ``controllers''.
def main_page(env):
    """
    Default page, calls main_view_page() with default view.
    """
    return main_view_page(env, 'default')


# TODO: Implement target filters.
def main_view_page(env, view):
    """
    Main page. Shows all torrents, per target.
    Does two XMLRPC calls per target.
    """
    if not loggedin_and_require(env):
        return handle_login(env)

    rtorrent_data = fetch_global_info()

    try:
        user_name = env['beaker.session']['user_name']
        user = lookup_user(user_name)
    except KeyError, e:
        user = None

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

            torrents[target['name']] = t.all()

        except InvalidTorrentException, e:
            return error_page(env, str(e))

    tmpl = jinjaenv.get_template('download_list.html')

    return template_render(tmpl, env, {'torrents_list' : torrents,
        'rtorrent_data' : rtorrent_data, 'view' : view} )

def error_page(env, error='No error?'):
    """
    Called on exceptions, when something goes wrong.
    """
    rtorrent_data = fetch_global_info()
    tmpl = jinjaenv.get_template('error.html')
    return template_render(tmpl, env, {'error' : error,
        'rtorrent_data' : rtorrent_data })

def torrent_info_page(env, torrent_hash, target):
    """
    Page for torrent information. Files, messages, active, etc.
    """
    if not loggedin_and_require(env):
        return handle_login(env)

    target = lookup_target(target)
    if target is None:
        return None # 404

    if not verify_target(env, target):
        return None # 404

    try:
        t = Torrent(target, torrent_hash)
        q = t.query()
        q.get_hash().get_name().get_size_bytes().get_download_total().\
                get_loaded_file().get_message().is_active()
        torrentinfo = q.all()[0] # .first() ?

    except InvalidTorrentException, e:
        return error_page(env, str(e))

    # FIXME THIS IS UGLY

    files = TorrentFileRequester(target, t._hash, '')\
            .get_path_components().all()

    files = map(lambda x: x['get_path_components'], files)

    tree = FileTree(files).root

    rtorrent_data = fetch_global_info()

    tmpl = jinjaenv.get_template('torrent_info.html')

    return template_render(tmpl, env, {'torrent' : torrentinfo,
        'tree' : tree, 'rtorrent_data' : rtorrent_data,
        'target' : target} )

def torrent_action(env, target, torrent_hash, action):
    """
    Start, Stop, Pause, Resume, Delete torrent.
    """
    if not loggedin_and_require(env):
        return handle_login(env)

    target = lookup_target(target)
    if target is None:
        return None # 404

    if not verify_target(env, target):
        return None # 404

    try:
        t = Torrent(target, torrent_hash)
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
    elif action == 'erase':
        t.erase()
    else:
        raise Exception('Invalid torrent action')

    # FIXME
    return 'lol'

def add_torrent_page(env, target):
    """
    Page for adding torrents.
    Works: Adding a correct torrent (URL only)
    What doesn't work:
        Error handling,
        Uploading .torrent files
        Option to add and start, or not start on add
    """
    if not loggedin_and_require(env):
        return handle_login(env)

    target = lookup_target(target)
    if target is None:
        return None # 404

    if not verify_target(env, target):
        return None # 404

    return_code = None

    # Check for POST vars
    if str(env['REQUEST_METHOD']) == 'POST':
        data = read_post_data(env)

        if 'torrent_url' in data:
            print "It's a URL!"
            torrent_url = data['torrent_url'].value
            if torrent_url:
                print "Loading URL:", torrent_url
                torrent_url = urllib.unquote_plus(torrent_url)
                response = urllib2.urlopen(torrent_url)
                torrent_raw = response.read()

                torrent_raw_bin = xmlrpclib.Binary(torrent_raw)

                rtorrent = RTorrent(target)
                return_code = rtorrent.add_torrent_raw(torrent_raw_bin)
        elif 'torrent_file' in data:
            print "It's a file!"
            # If someone is messing around with the forms, check for it
            if not data['torrent_file'].file:
                return "Error: Form field 'torrent_file' not a file!"

            print "Loading file:", data['torrent_file'].filename
            torrent_raw_bin = xmlrpclib.Binary(data['torrent_file'].value)

            rtorrent = RTorrent(target)
            return_code = rtorrent.add_torrent_raw(torrent_raw_bin)
        else:
            return str("Error: Invalid POST data")

    rtorrent_data = fetch_global_info()

    tmpl = jinjaenv.get_template('torrent_add.html')

    if return_code == 0:
        torrent_added = 'SUCCES'
    elif return_code is not None:
        torrent_added = 'FAIL'
    else:
        torrent_added = ''

    return template_render(tmpl, env, {'rtorrent_data' : rtorrent_data,
        'torrent_added': torrent_added, 'target' : target['name'] } )

def torrent_file(env, target, torrent_hash):
    """
    """
    if not loggedin_and_require(env):
        return handle_login(env)

    target = lookup_target(target)
    if target is None:
        return None # 404

    if not verify_target(env, target):
        return None # 404

    try:
        r = RTorrent(target)
        t = Torrent(target, torrent_hash)
        filepath = t.get_loaded_file()

        # TODO: Check for errors. (Permission denied, non existing file, etc)
        contents = r.execute_command('sh', '-c', 'cat ' + filepath + \
                ' | base64')

    except InvalidTorrentException, e:
        return error_page(env, str(e))

    return ['application/x-bittorrent', base64.b64decode(contents)]


def static_serve(env, static_file):
    """
    Serve static files ourselves. Most browsers will cache them after one
    request anyway, so there's not a lot of overhead.
    """
    mimetype = mimetypes.guess_type('./static/' + static_file)
    if mimetype[0] == None:
        return None

    # print 'Serving static file:', static_file, 'with mime type:', mimetype[0]

    try:
        f = open('./static/' + static_file)
        return [mimetype[0], f.read()]
    except IOError:
        return None

def style_serve(env):
    tmpl = jinjaenv.get_template('style.css')

    background = BACKGROUND_IMAGE

    try:
        user_name = env['beaker.session']['user_name']
        user = lookup_user(user_name)
    except KeyError, e:
        user = None

    if user:
        background = user.background_image

    return ['text/css', template_render(tmpl, env,
            {'background_image' : background})]

def handle_login(env):
    tmpl = jinjaenv.get_template('loginform.html')

    if str(env['REQUEST_METHOD']) == 'POST':
        data = read_post_data(env)

        if 'user' not in data or 'pass' not in data:
            return template_render(tmpl, env,
            {   'session' : env['beaker.session'], 'loginfail' : True}  )

        user = urllib.unquote_plus(data['user'].value)
        pass_ = urllib.unquote_plus(data['pass'].value)

#        pass = hashlib.sha256(pass).hexdigest()
        u = lookup_user(user)
        if u is None:
            return template_render(tmpl, env,
            {   'session' : env['beaker.session'], 'loginfail' : True}  )

        if u.password == pass_:
            env['beaker.session']['user_name'] = user
            env['beaker.session'].save()
            return main_page(env)
        else:
            return template_render(tmpl, env,
            {   'session' : env['beaker.session'], 'loginfail' : True}  )

    return template_render(tmpl, env, { })

def handle_logout(env):
    if loggedin(env):
        s = env['beaker.session']
        s.delete()
    else:
        return error_page(env, 'Not logged in')

    return main_page(env)

def parse_config():
    """
    Use lib.config_parser to parse each target in the rtorrent_config dict.
    I suppose it's more like verifying than parsing. Returns a list of dicts,
    one dict per target.
    """

    targets = []
    for x in rtorrent_config:
        try:
            info = parse_config_part(rtorrent_config[x], x)
        except RTorrentConfigException, e:
            print 'Invalid config: ', e
            sys.exit(1)

        targets.append(info)

    return targets

def parse_users():
    """
    """
    users = []
    for x in torrent_users:
        try:
            user = parse_user_part(torrent_users[x], x)
        except RTorrentConfigException, e:
            print 'Invalid config: ', e
            sys.exit(1)

        users.append(user)

    return users

session_options = {
    'session.cookie_expires' : True
}

if __name__ == '__main__':
    targets = parse_config()
    users = parse_users()
    jinjaenv = Environment(loader=PackageLoader('pyrotorrent', 'templates'))
    jinjaenv.autoescape = True
    wt = WebTool()

    session_options = {
        'session.cookie_expires' : True
    }

    # Add all rules
    execfile('rules.py')

    app = pyroTorrentApp
    app = SessionHack(app, error_page)
    app = SessionMiddleware(app, session_options)

    if USE_OWN_HTTPD:
        from wsgiref.simple_server import make_server
        httpd = make_server('', 8000, app)
        httpd.serve_forever()
    else:
        from flup.server.fcgi import WSGIServer
        WSGIServer(app).run()
