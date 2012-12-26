#!/usr/bin/env python
"""
TODO:
    -   Default arguments for jinja (wn, etc)
"""

###############################################################################
#                               PYROTORRENT                                   #
###############################################################################
# To configure pyrotorrent, check the documentation as well as config.py and  #
# flask-config.py. These two files will be merged later.                      #
###############################################################################


from flask import Flask, request, session, g, redirect, url_for, \
             abort, render_template, flash

from flask import Response

# TODO http://flask.pocoo.org/docs/config/


app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_pyfile('flask-config.py')

from config import FILE_BLOCK_SIZE, BACKGROUND_IMAGE, \
        USE_AUTH, ENABLE_API, rtorrent_config, torrent_users, USE_OWN_HTTPD, \
        CACHE_TIMEOUT

from lib.config_parser import parse_config_part, parse_user_part, \
    RTorrentConfigException, CONNECTION_SCGI, CONNECTION_HTTP

from model.rtorrent import RTorrent
from model.torrent import Torrent

from lib.multibase import InvalidTorrentException, InvalidConnectionException, \
    InvalidTorrentCommandException

from lib.torrentrequester import TorrentRequester
from lib.peerrequester import PeerRequester

from lib.filerequester import TorrentFileRequester
from lib.filetree import FileTree

# TODO REMOVE?
from lib.helper import wiz_normalise, pyro_render_template, error_page, loggedin, \
    loggedin_and_require, parse_config, parse_users, fetch_user, \
    fetch_global_info, lookup_user, lookup_target, redirect_client_prg, \
    redirect_client
from lib.decorators import pyroview, require_torrent, \
    require_rtorrent, require_target

# For MIME
import mimetypes

# For stat and path services
import os
import stat

# For fetching http .torrents
import urllib2
import xmlrpclib # for .Binary

# For serving .torrent files
import base64

import datetime
import time

import json

@app.route('/')
@app.route('/view/<view>')
@pyroview
def main_view_page(view='default'):
    rtorrent_data = fetch_global_info()

#    if view not in rtorrent_data.get_view_list:
#        return error_page(env, 'Invalid view: %s' % view)

    torrents = {}
    for target in targets:
        if g.user == None and USE_AUTH:
            continue
        if g.user and (target['name'] not in g.user.targets):
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

            cache.set(h, torrents[target['name']], timeout=CACHE_TIMEOUT)

        except InvalidTorrentException, e:
            return error_page(env, str(e))

    return pyro_render_template('download_list.html',
            torrents_list=torrents, rtorrent_data=rtorrent_data, view=view
            # TODO
            )

@app.route('/target/<target>/torrent/<torrent>')
@app.route('/target/<target>/torrent/<torrent>/<action>')
@pyroview
@require_target
@require_torrent
def torrent_info(target, torrent, action=None):
    print torrent, action
    if action in ('open', 'close', 'start', 'stop', 'pause', 'resume'):
        print 'Executing action', action
        print getattr(torrent, action)()
        flash('Executed %s on torrent %s' % (action, torrent.get_name()))

    try:
        q = torrent.query()
        q.get_hash().get_name().get_size_bytes().get_download_total().\
                get_loaded_file().get_message().is_active()
        h = hash(q)

        torrentinfo = cache.get(h)
        if torrentinfo is None:
            torrentinfo = q.all()[0] # .first() ?
            cache.set(h, torrentinfo, CACHE_TIMEOUT)

    except InvalidTorrentException, e:
        return error_page(env, str(e))

    p = PeerRequester(torrent.target, torrent._hash)

    p.get_address().get_client_version().is_encrypted().get_id()

    peers = p.all()

    files = TorrentFileRequester(target, torrent._hash)\
            .get_path_components().get_size_chunks().get_completed_chunks()

    h = hash(files)
    f = cache.get(h)
    if f is None:
        f = files.all()
        cache.set(h, f, CACHE_TIMEOUT)

    tree = FileTree(f).root

    rtorrent_data = fetch_global_info()

    return pyro_render_template('torrent_info.html', torrent=torrentinfo, tree=tree,
        rtorrent_data=rtorrent_data, target=target,
        file_downloads=target.has_key('storage_mode'),
        peers=peers

        # TODO FIX ME
        ,wn=wiz_normalise
    )

@app.route('/target/<target>/torrent/<torrent>/peer/<peer_id>')
@pyroview
@require_target
@require_torrent
def peer_info(target, torrent, peer_id):
    return 'Peer info page will be here'

@app.route('/target/<target>/torrent/<torrent>.torrent')
@pyroview
@require_target
@require_torrent
@require_rtorrent
def torrent_file(target, torrent, rtorrent):
    try:
        filepath = torrent.get_loaded_file()

        # TODO: Check for errors. (Permission denied, non existing file, etc)
        contents = rtorrent.execute_command('sh', '-c', 'cat ' + filepath +
                ' | base64')

    except InvalidTorrentException, e:
        return error_page(env, str(e))

    r = Response(base64.b64decode(contents),
            mimetype='application/x-bittorrent')
    r.status_code = 200
    return r

@app.route('/target/<target>/torrent/<torrent>/get_file/<path:filename>')
@pyroview
@require_target
@require_torrent
def torrent_get_file(target, torrent, filename):
    # Is file fetching enabled?
    print target
    if not target.has_key('storage_mode'):
        print "File fetching disabled, 404"
        abort(404)

    s_mode = target['storage_mode']

    print "Requested file:", filename

    # Fetch absolute path to torrent
    try:
        # FIXME: rtorrent get_full_path() apparently isn't always ``full''.
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
        print "Exception performing stat:", e
        abort(500)

    print "Computed path:", file_path

    # Now verify this path is within torrent path
    if file_path.find(t_path) != 0:
        print "Path rejected.."
        abort(403)

    print "Path accepted."

    HTTP_RANGE_REQUEST = False
    try:
        _bytes = request.headers['Range']
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
        headers.append(('Content-length', str(_end-_start)))
    else:
        headers.append(('Content-length', str(f_size)))

        # Let browser figure out filename
        # See also: http://greenbytes.de/tech/tc2231/
        # and: http://stackoverflow.com/questions/1361604/how-to-encode-utf8-filename-for-http-headers-python-django
        headers.append(('Content-Disposition', 'attachment;'\
            'filename="'+os.path.split(file_path)[1]+'"'))

    # Useful code for returning files
    # http://stackoverflow.com/questions/3622675/returning-a-file-to-a-wsgi-get-request
#    if 'wsgi.file_wrapper' in env:
#        f_ret = env['wsgi.file_wrapper'](f, FILE_BLOCK_SIZE)
#    else:
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

        r = Response(f_ret)
        r.status_code = 206
        r.headers = headers
        return r
    else:
        r = Response(f_ret)
        r.status_code = 200
        r.headers = headers
        return r


@app.route('/target/<target>/add_torrent', methods=['GET', 'POST'])
@pyroview
@require_target
def add_torrent_page(target):
    if request.method == 'POST':
        if 'torrent_file' in request.files:

            torrent_raw = request.files['torrent_file'].read()

            torrent_raw_bin = xmlrpclib.Binary(torrent_raw)

            rtorrent = RTorrent(target)
            return_code = rtorrent.add_torrent_raw_start(torrent_raw_bin)
        elif 'torrent_url' in request.form:

            torrent_url = request.form['torrent_url']

            response = urllib2.urlopen(torrent_url)
            torrent_raw = response.read()

            torrent_raw_bin = xmlrpclib.Binary(torrent_raw)

            rtorrent = RTorrent(target)
            return_code = rtorrent.add_torrent_raw_start(torrent_raw_bin)
        elif 'magnet' in request.form:
            magnet_link = request.form['magnet']

            torrent = 'd10:magnet-uri' + str(len(magnet_link)) + ':' + magnet_link + 'e'

            rtorrent = RTorrent(target)
            return_code = rtorrent.add_torrent_raw(torrent)

        flash('Succesfully added torrent' if return_code == 0 else 'Failed to add torrent')

    rtorrent_data = fetch_global_info()

    return pyro_render_template('torrent_add.html',
            rtorrent_data=rtorrent_data, target=target['name'])

def handle_api_method(method, keys):
    if not ENABLE_API:
        return None
    if method not in known_methods:
        raise Exception('Unknown method')

    if 'target' in keys:
        target = keys['target']
        target = lookup_target(target)
        if target is None:
            print 'Returning null, target is invalid'
            return None

#    u = fetch_user(env)
#    # User can't be none, since we've already passed login.
#    if USE_AUTH and target not in user.targets:
#        print 'User is not allowed to use target: %s!' % target


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

        h = hash(tr)
        r = cache.get(h)
        if r is None:
            r = tr.all()
            cache.set(h, r, timeout=CACHE_TIMEOUT)

        return r

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
            getattr(a, method)(*args)

        h = hash(a)
        r = cache.get(h)
        if r is None:
            r = a.first()
            cache.set(h, r, timeout=CACHE_TIMEOUT)

        return r
    except (InvalidTorrentException, InvalidTorrentCommandException), e:
        print e
        return None

known_methods = {
    'torrentrequester' : handle_torrentrequester,
    'rtorrent' : handle_rtorrent_torrent,
    'torrent' : handle_rtorrent_torrent
}


@app.route('/api', methods=['POST'])
def api():
    if not ENABLE_API:
        abort(403)
    #if not loggedin_and_require(env):
    #    r = Response(json.dumps(None, indent=' ' * 4), mimetype='application/json')
    #    r.status_code = 403
    #    return r

    # Get JSON request via POST data
    try:
        req = request.form['request']
    except KeyError, e:
        abort(500)

    d = json.loads(req)
    resp = []

    for x in d:
        if 'type' in x:
            print 'Method:', x['type']
            resp.append(handle_api_method(x['type'], x))

    s = json.dumps(resp, indent=4)

    r = Response(s, mimetype='application/json')
    r.status_code = 200
    return r

@app.route('/style.css')
def style_serve():
    """
    TODO: Re-add user lookup and user specific image:

    if user and user.background_image != None:
        background = user.background_image

    """
    background = BACKGROUND_IMAGE

    return Response(pyro_render_template('style.css',
        trans=0.6),
        mimetype='text/css')

@app.route('/login', methods=['GET', 'POST'])
@pyroview(require_login=False)
def handle_login():
    print 'Handle das login'
    #tmpl = jinjaenv.get_template('loginform.html')
    _login_fail = lambda: pyro_render_template('loginform.html', loginfail=True)
    print 'Request method:', request.method

    if request.method == 'POST':
        if 'user' not in request.form or 'pass' not in request.form:
            return _login_fail()

        user = request.form['user']
        passwd = request.form['pass']

#        pass = hashlib.sha256(pass).hexdigest()
        u = lookup_user(user)
        if u is None:
            return _login_fail()

        if u.password == passwd:
            print 'Login succes.'
            session['user_name'] = user

            # Redirect user to original page, or if not possible
            # to the main page.
            redir_url = session.pop('login_redirect_url', None)
            if redir_url:
                print 'Redirecting to:', redir_url
                return redirect_client_prg(url=redir_url)

            return redirect_client_prg('main_view_page')

        else:
            return _login_fail()

    # Not logged in?
    # Render login page, and store
    # current URL in beaker session.
    if not loggedin():
        print 'Not logged in, storing session data:', request.base_url
        session['login_redirect_url'] = request.base_url

        return pyro_render_template('loginform.html')

    # User already loggedin, redirect to main page.
    else:
        return redirect_client('main_view_page')

@app.route('/logout')
@pyroview(require_login=False)
def handle_logout():
    if loggedin():
        session.pop('user_name', None)
    else:
        return error_page(env, 'Not logged in')

    return redirect_client('main_view_page')

class PrefixWith(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        app_root = app.config['APPLICATION_ROOT']
        if environ['PATH_INFO'].startswith(app_root):
            environ['PATH_INFO'] = environ['PATH_INFO'][len(app_root):]
            environ['SCRIPT_NAME'] = app_root
        else:
            environ['PATH_INFO'] = '/GENERIC-404'
            environ['SCRIPT_NAME'] = ''
            #start_response('404 Not Found', [('Content-Type', 'text/plain')])
            #return '404'

        return app(environ, start_response)



class SimpleCache(object):
    def __init__(self):
        self.kv = {}

    def get(self, name):
        if name in self.kv:
            v = self.kv[name]
            tt = (time.time() - v[1])
            if tt > v[2]:
                return None
            return v[0]
        else:
            return None

    def set(self, name, value, timeout=1):
        self.kv[name] = (value, time.time(), timeout)



if __name__ == '__main__':
    targets = parse_config()
    users = parse_users()

    from werkzeug.contrib.cache import SimpleCache
    cache = SimpleCache()

    import lib.helper
    lib.helper.targets = targets
    lib.helper.users = users
    lib.helper.cache = cache
    lib.decorators.handle_login = handle_login


    if USE_OWN_HTTPD:
        app.run() # Run with host='0.0.0.0' if you want pyro to be
                                # remotely accessible
    else:
        application = PrefixWith(app)
        from flup.server.fcgi import WSGIServer
        WSGIServer(application).run()
