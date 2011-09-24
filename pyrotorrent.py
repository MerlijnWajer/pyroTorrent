#!/usr/bin/env python
"""
pyroTorrent module.
"""

from jinja2 import Environment, PackageLoader

from lib.webtool import WebTool, read_post_data

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

import simplejson as json

# For sys.exit(), etc
import sys

from config import BASE_URL, STATIC_URL, FILE_BLOCK_SIZE, BACKGROUND_IMAGE, \
        USE_AUTH, ENABLE_API, rtorrent_config, torrent_users
try:
    from config import USE_OWN_HTTPD
except ImportError:
    USE_OWN_HTTPD = False # sane default?

from lib.config_parser import parse_config_part, parse_user_part, \
    RTorrentConfigException, CONNECTION_SCGI, CONNECTION_HTTP

from lib.sessionhack import SessionHack, SessionHackException

from model.rtorrent import RTorrent
from model.torrent import Torrent

from lib.multibase import InvalidTorrentException, InvalidConnectionException, \
    InvalidTorrentCommandException

from lib.torrentrequester import TorrentRequester
from lib.filerequester import TorrentFileRequester
from lib.filetree import FileTree

from lib.helper import wiz_normalise, template_render, error_page, loggedin, \
    loggedin_and_require, parse_config, parse_users, fetch_user, \
    fetch_global_info, lookup_user
from lib.decorator import webtool_callback, require_torrent, \
    require_rtorrent, require_target

# For MIME
import mimetypes

# For stat and path services
import os
import stat

import datetime
import time

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

    elif type(r) in (tuple, list) and len(r) == 3:
        # Respond with custom headers
        start_response(r[0], r[1])
        r = r[2]

    # 200
    else:
        start_response('200 OK', [('Content-Type', 'text/html;charset=utf8')])

    # Response data

    # If r is not a file, but a string
    # prevent an exhausting loop
    if type(r) == str:
        return [r]

    return r

# These *_page functions are what you would call ``controllers''.
@webtool_callback(
    require_login = False,
    do_lookup_user = True
    )
def main_page(env, user):
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

    user = fetch_user(env)

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

@webtool_callback
@require_target
@require_torrent
def torrent_info_page(env, target, torrent):
    """
    Page for torrent information. Files, messages, active, etc.
    """

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

    tmpl = jinjaenv.get_template('torrent_info.html')

    return template_render(tmpl, env, {'torrent' : torrentinfo,
        'tree' : tree, 'rtorrent_data' : rtorrent_data,
        'target' : target, 'file_downloads' : target.has_key('storage_mode')})

@webtool_callback
@require_target
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

    try:
        user_name = env['beaker.session']['user_name']
        user = lookup_user(user_name)
    except KeyError, e:
        user = None

    if USE_AUTH:
        if user == None or target['name'] not in user.targets:
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
        'torrent_added' : torrent_added, 'target' : target['name']} )

@webtool_callback
@require_target
@require_torrent
@require_rtorrent
def torrent_file(env, target, torrent, rtorrent):
    """
    This function returns a torrent's
    .torrent file to the user.
    """

    try:
        filepath = torrent.get_loaded_file()

        # TODO: Check for errors. (Permission denied, non existing file, etc)
        contents = rtorrent.execute_command('sh', '-c', 'cat ' + filepath +
                ' | base64')

    except InvalidTorrentException, e:
        return error_page(env, str(e))

    headers = [('Content-Type', 'application/x-bittorrent')]
    return ['200 OK', headers, base64.b64decode(contents)]

# Download a file contained in a torrent
@webtool_callback
@require_target
@require_torrent
def torrent_get_file(env, target, torrent, filename):
    """
    Download a file contained within a torrent.

    env:            The WSGI environment
    target:         The target bittorrent client
    torrent_hash:   Hash of the torrent being examined
    filename:       path to file within torrent
                    (should not start with a /)
    """

    # Is file fetching enabled?
    print target
    if not target.has_key('storage_mode'):
        print "File fetching disabled, 404"
        return None
    s_mode = target['storage_mode']

    print "Requested file (un-unquoted):", filename
    filename = urllib.unquote_plus(filename)
    print "Requested file:", filename

    # Fetch absolute path to torrent
    try:
        t_path = torrent.get_full_path()
    except InvalidTorrentException, e:
        return error_page(env, str(e))

    # rtorrent is running on a remote fs mounted
    # on this machine?
    if 'remote_path' in s_mode:
        # Transform remote path to locally mounted path
        t_path = t_path.replace(s_mode['remote_path'], s_mode['local_path'], 1)

    # Compute absolute file path
    try:
        if stat.S_ISDIR(os.stat(t_path).st_mode):
            print "Multi file torrent."
            file_path = os.path.abspath(t_path + '/' + filename)
        else:
            print "Single file torrent."
            file_path = os.path.abspath(t_path)
    except OSError as e:
        print "Exception performing stat:"
        print e
        return None

    print "Computed path:", file_path

    # Now verify this path is within torrent path
    if file_path.find(t_path) != 0:
        print "Path rejected.."
        return None
    print "Path accepted."

    HTTP_RANGE_REQUEST = False
    try:
        _bytes = env['HTTP_RANGE']
        print 'HTTP_RANGE Found'
        _bytes = _bytes.split('=')[1]
        _start, _end = _bytes.split('-')
        _start = int(_start)
        if _end:
            _end = int(_end)

        HTTP_RANGE_REQUEST = True

    except KeyError, e:
        print 'No HTTP_RANGE passed'
    except (ValueError, IndexError), e:
        print 'Invalid HTTP_RANGE:', e


    # Open file for reading
    try:
        f = open(file_path, 'r')
        if HTTP_RANGE_REQUEST:
            print 'Seeking...'
            f.seek(_start)
    except IOError as e:
        print 'Exception opening file:', e
        return None
    print 'File open.'

    # Setup response
    f_size = os.path.getsize(file_path)
    if HTTP_RANGE_REQUEST:
        # We can't set _end earlier.
        if not _end:
            _end = f_size

    mimetype = mimetypes.guess_type(file_path)
    if mimetype[0] == None:
        mimetype = 'application/x-binary'
    else:
        mimetype = mimetype[0]

    headers = []
    headers.append(('Content-Type', mimetype))

    if HTTP_RANGE_REQUEST:
        headers.append(('Content-length', str(_end-_start+1)))
    else:
        headers.append(('Content-length', str(f_size)))

        # Let browser figure out filename
        # See also: http://greenbytes.de/tech/tc2231/
        # and: http://stackoverflow.com/questions/1361604/how-to-encode-utf8-filename-for-http-headers-python-django
        headers.append(('Content-Disposition', 'attachment;'\
            'filename='+os.path.split(file_path)[1]))

    # Useful code for returning files
    # http://stackoverflow.com/questions/3622675/returning-a-file-to-a-wsgi-get-request
    if 'wsgi.file_wrapper' in env:
        f_ret = env['wsgi.file_wrapper'](f, FILE_BLOCK_SIZE)
    else:
        f_ret = iter(lambda: f.read(FILE_BLOCK_SIZE), '')


    if HTTP_RANGE_REQUEST:
        # Date, Content-Location/ETag, Expires/Cache-Control
        # Either a Content-Range header field (section 14.16) indicating
        # the range included with this response, or a multipart/byteranges
        # Content-Type including Content-Range fields for each part. If a
        # Content-Length header field is present in the response, its
        # value MUST match the actual number of OCTETs transmitted in the
        # message-body.
        d = datetime.datetime.now()

        headers.append(('Date', d.strftime('%a, %d %b %Y %H:%M:%S GMT')))
        headers.append(('Content-Range', 'bytes: %d-%d/%d' % (_start, _end-1,
            f_size-1)))
        headers.append(('Cache-Control', 'max-age=3600'))
        headers.append(('Content-Location', filename))

        print headers
        return ('206 Partial Content', headers, f_ret)
    else:
        print headers
        return ('200 OK', headers, f_ret)

@webtool_callback(
    require_login = False
    )
def static_serve(env, static_file):
    """
    Serve static files ourselves. Most browsers will cache them after one
    request anyway, so there's not a lot of overhead.
    """
    mimetype = mimetypes.guess_type('./static/' + static_file)
    if mimetype[0] == None:
        return None

    pyropath = os.path.abspath(__file__)
    filepath = os.path.abspath('./static/' + static_file)
    pyrodir =  os.path.dirname(pyropath) + '/static'

    if not filepath.startswith(pyrodir):
        return None

    # print 'Serving static file:', static_file, 'with mime type:', mimetype[0]

    try:
        st = os.stat('./static/' + static_file)
        d = datetime.datetime.fromtimestamp(st[stat.ST_MTIME])

        headers = [('Content-Type', mimetype[0]),
                   ('Last-Modified', d.strftime('%a, %d %b %Y %H:%M:%S GMT'))
                   ]

        if 'HTTP_IF_MODIFIED_SINCE' in env:
            try:
                prev_date = datetime.datetime.strptime( \
                        env['HTTP_IF_MODIFIED_SINCE'], \
                        '%a, %d %b %Y %H:%M:%S GMT')
                if prev_date >= d:
                    return ['304 Not Modified', headers, '']
            except ValueError, e:
                pass

        f = open('./static/' + static_file)
        return ['200 OK', headers, f.read()]
    except (IOError, OSError):
        return None

@webtool_callback(
    require_login = False,
    do_lookup_user = True
    )
def style_serve(env, user):
    tmpl = jinjaenv.get_template('style.css')

    background = BACKGROUND_IMAGE

    if user and user.background_image != None:
        background = user.background_image

    headers = [('Content-Type', 'text/css')]
    return ['200 OK', headers, template_render(tmpl, env,
            {'background_image' : background})]

@webtool_callback(
    require_login = False
    )
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

@webtool_callback(
    require_login = False
    )
def handle_logout(env):
    if loggedin(env):
        s = env['beaker.session']
        s.delete()
    else:
        return error_page(env, 'Not logged in')

    return main_page(env)


def handle_api_method(env, method, keys):
    if method not in known_methods:
        raise Exception('Unknown method')

    if 'target' in keys:
        target = k['target']
        target = lookup_target(target)
        if target is None:
            print 'Returning null, target is invalid'
            return None

    u = fetch_user(env)
    # User can't be none, since we've already passed login.
    if USE_AUTH and target not in user.targets:
        print 'User is not allowed to use target: %s!' % target


    if method == 'torrentrequester':
        return known_methods[method](keys, target)
    else:
        return known_methods[method](keys, method, target)


def handle_torrentrequester(k, target):
    if 'view' not in k or 'attributes' not in k:
        return None

    view = k['view']
    attributes = k['attributes']

    try:
        tr = TorrentRequester(target, view)
        for method, args in attributes:
            getattr(tr, method)

        return tr.all()

    except (InvalidTorrentCommandException,):
        return None


def handle_rtorrent_torrent(k, m, target):
    if 'attributes' not in k:
        return None

    attributes = k['attributes']

    try:
        if m == 'rtorrent':
            a = RTorrent(target).query()
        else:
            if 'hash' not in k:
                return None

            _hash = k['hash']

            a = Torrent(target, _hash).query()

        for method, args in attributes:
            getattr(a, method)(args)

        return a.first()
    except (InvalidTorrentException, InvalidTorrentCommandException):
        return None

known_methods = {
    'torrentrequester' : handle_torrentrequester,
    'rtorrent' : handle_rtorrent_torrent,
    'torrent' : handle_rtorrent_torrent
}

def handle_api(env):
    """
    """
    if str(env['REQUEST_METHOD']) != 'POST':
        return None

    if not loggedin_and_require(env):
        return ['403 Forbidden', [('Content-Type', 'application/json')],
                json.dumps(None, indent=' ' * 4)]

    # Get JSON request via POST data
    data = read_post_data(env)
    request = urllib.unquote_plus(data['request'].value)

    print 'Request:', repr(request)

    d = json.loads(request)
    r = []

    for x in d:
        if 'type' in x:
            print 'Method:', x['type']
            r.append(env, handle_api_method(x['type'], x))

    return ['200 OK', [('Content-Type', 'application/json')], \
            json.dumps(r, indent=' ' * 4)]


session_options = {
    'session.cookie_expires' : True
}

if __name__ == '__main__':
    targets = parse_config()
    users = parse_users()

    jinjaenv = Environment(loader=PackageLoader('pyrotorrent', 'templates'))
    jinjaenv.autoescape = True
    wt = WebTool()

    # O GOD WTF
    # I apologise deeply for these inconsiderate workarounds ;-)
    import lib.helper
    lib.helper.targets = targets
    lib.helper.users = users
    lib.helper.jinjaenv = jinjaenv
    import lib.decorator
    lib.decorator.handle_login = handle_login

    session_options = {
        'session.cookie_expires' : True
    }

    # Add all rules
    execfile('rules.py')

    app = pyroTorrentApp
    app = SessionHack(app, error_page)
    app = SessionMiddleware(app, session_options)

    if USE_OWN_HTTPD:
        from wsgiref.simple_server import make_server, \
                WSGIServer, WSGIRequestHandler
        WSGIRequestHandler.log_message = lambda *x: None
        httpd = make_server('', 8000, app, server_class=WSGIServer,
                handler_class=WSGIRequestHandler)
        httpd.serve_forever()
    else:
        from flup.server.fcgi import WSGIServer
        WSGIServer(app).run()

