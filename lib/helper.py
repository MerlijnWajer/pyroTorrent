"""
Various helper functions
"""

import sys

# flask webframework stuff
from flask import redirect, g, session, url_for, render_template

# pyro imports
from config import FILE_BLOCK_SIZE, BACKGROUND_IMAGE, \
        USE_AUTH, ENABLE_API, rtorrent_config, torrent_users
from lib.config_parser import parse_config_part, parse_user_part, \
    RTorrentConfigException, CONNECTION_SCGI, CONNECTION_HTTP
from lib.multibase import InvalidTorrentException, InvalidConnectionException, \
    InvalidTorrentCommandException
from model.rtorrent import RTorrent

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

def error_page(error='No error?'):
    """
    Called on exceptions, when something goes wrong.
    """
    rtorrent_data = fetch_global_info()
    tmpl = jinjaenv.get_template('error.html')
    return template_render(tmpl, {'error' : error,
        'rtorrent_data' : rtorrent_data })

# Is session in login state?
def loggedin():
   return 'user_name' in session

# Logged in when required?
# XXX: 'authorized' might be a better name for this function
# since having authorisation does not imply being logged in.
def loggedin_and_require():
    """
        Return False whenever the user is not logged in and
        this is a requirement.
        True otherwise.
    """
    return loggedin() if USE_AUTH else True

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
    Verify username is in configfile.
    """

    for x in users:
        if x.name == name:
            return x
    return None

# The following 2 functions are used by the decorator subsystem
# to handle passing deep function objects. Deep functions in pyroTorrent are the
# original undecorated functions.

# XXX These functions have been superseded by the use of the wraps decorator
# and will be removed in the (near) future.

def detach_deep_func(func):
    """
    This function retrieves a deep function object asociated with a returned
    decorated function object. This function is called 'detach' and not 'fetch'
    because it also removes the asociation after retrieving. We do this to
    decrease the number of references to the original function and have only
    the last returned function point directly to the deep function.

    At the moment deep functions are stored in the _PYRO_deep_func attribute.

    returns: deep function (Python function object)
    """

    if hasattr(func, '_PYRO_deep_func'):
        deep_func = func._PYRO_deep_func
        del func._PYRO_deep_func
        return deep_func

    # This function has no deep function attribute and is therefore
    # most likely the original function and thus 'deep function'
    return func

def attach_deep_func(func, deep_func):
    """
    Attach a deep function object to a decorated function.

    returns: 'func' argument.
    """

    # Attaching a deep function to a deep function..
    # not such a good idea, return unmodified function.
    if func is not deep_func:
        func._PYRO_deep_func = deep_func

    return func

# Function to render the jinja template and pass some simple vars / functions.
def pyro_render_template(template, **kw):
    """
        Template Render is a helper that initialises basic template variables
        and handles unicode encoding.
    """
    #XXX Base URL not needed any more since Flask
    kw['use_auth'] = USE_AUTH
    kw['wn'] = wiz_normalise
    kw['trans'] = 0.4
    kw['login'] = session['user_name'] if \
        session.has_key('user_name') else None

    #ret = unicode(template.render(vars)).encode('utf8')

    return render_template(template, **kw)

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

            h = hash(r)
            res[target['name']] = cache.get(h)
            if res[target['name']]:
                continue

            res[target['name']] = r.first()
            cache.set(h, res[target['name']], timeout=60)

        except InvalidConnectionException, e:
            print 'InvalidConnectionException:', e
            # Do we want to return or just not get data for this target?
            # I'd say return for now.
            return {}

    return res

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

def fetch_user():
    """
    Unconditionally fetch credentials from the flask session,
    and verify against config file.
    returns: 
        A valid user string, or None if no valid user could be found.
    """
    try:
        user_name = session['user_name']
        user = lookup_user(user_name)
    except KeyError, e:
        user = None
    return user

def parse_args_to_url(endpoint=None, url=None, **kw):
    """
    This function parses the arguments accepted by the pyroTorrent
    redirect helpers.

    Arguments:
        This function accepts only keyword arguments or a single
        endpoint string as first argument.

        enpoint:
            A Flask/Werkzeug endpoint to be redirected to.

        url:
            A URL to be redirected to in any format you fancy.

        **kw:
            Any variables provided to the endpoint.
            For instance a route of: '/view/<name>' would
            accept a 'name' keyword.

    Returns:
        A URL string.

    Raises:
        ValueError:
            When either both endpoint and url specify something
            or whenever both a URL and additional keyword arguments
            are provided.
    """

    if endpoint and url:
        raise ValueError("Both 'endpoint' and 'URL' have valid values," +
            "only specify one of them.")

    if endpoint:
        return url_for(endpoint, **kw)

    if url and len(kw):
        raise ValueError('Cannot specify keyword arguments for fixed URL')

    return url

def redirect_client_prg(endpoint=None, **kw):
    """
    Return a HTTP 303 response, effectively redirecting
    the client to the given URL in a Post/Redirect/Get manor.

    Arguments:
        This function accepts only keyword arguments or a single
        endpoint string as first argument.

        enpoint:
            A Flask/Werkzeug endpoint to be redirected to.

        url:
            A URL to be redirected to in any format you fancy.

        **kw:
            Any variables provided to the endpoint.
            For instance a route of: '/view/<name>' would
            accept a 'name' keyword.

    Returns:
        A Flask Response object.

    Raises:
        ValueError:
            When either both endpoint and url specify something
            or whenever both a URL and additional keyword arguments
            are provided.
    """

    url = parse_args_to_url(endpoint, **kw)
    print 'redirect_client_prg:', url

    # Tell flask to redirect using HTTP 303 See Other.
    # A 303 should not result in resubmission of POST data
    # to the given location.
    return redirect(url, code=303)

def redirect_client(endpoint=None, **kw):
    """
    Return a HTTP 307 response, effectively redirecting
    the client to the given URL.

    Arguments:
        This function accepts only keyword arguments or a single
        endpoint string as first argument.

        enpoint:
            A Flask/Werkzeug endpoint to be redirected to.

        url:
            A URL to be redirected to in any format you fancy.

        **kw:
            Any variables provided to the endpoint.
            For instance a route of: '/view/<name>' would
            accept a 'name' keyword.

    Returns:
        A Flask Response object.

    Raises:
        ValueError:
            When either both endpoint and url specify something
            or whenever both a URL and additional keyword arguments
            are provided.
    """

    url = parse_args_to_url(endpoint, **kw)
    print 'redirect_client:', url

    # Tell flask to redirect using HTTP 307 Temporary Redirect.
    # A 307 should not be cached unless explicitely stated so
    # by the HTTP headers.
    return redirect(url, code=307)

