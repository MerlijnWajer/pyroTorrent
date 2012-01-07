"""
Various helper functions
"""

import sys
from config import BASE_URL, STATIC_URL, FILE_BLOCK_SIZE, BACKGROUND_IMAGE, \
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

def error_page(env, error='No error?'):
    """
    Called on exceptions, when something goes wrong.
    """
    rtorrent_data = fetch_global_info()
    tmpl = jinjaenv.get_template('error.html')
    return template_render(tmpl, env, {'error' : error,
        'rtorrent_data' : rtorrent_data })

# Is environment in login state?
def loggedin(env):
   return 'user_name' in env['beaker.session']

# Require login?
def loggedin_and_require(env):
    if USE_AUTH:
        return loggedin(env)
    else:
        return True

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
def template_render(template, env, vars):
    """
        Template Render is a helper that initialises basic template variables
        and handles unicode encoding.
    """
    vars['base_url'] = BASE_URL
    vars['static_url'] = STATIC_URL
    vars['use_auth'] = USE_AUTH
    vars['wn'] = wiz_normalise
    vars['trans'] = 0.4
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

def fetch_user(env):
    """
    Unconditionally fetch credentials from the passed environment,
    and verify against config file.
    returns: 
        A valid user string, or None if no valid user could be found.
    """
    try:
        user_name = env['beaker.session']['user_name']
        user = lookup_user(user_name)
    except KeyError, e:
        user = None
    return user

def redirect_client_prg(url):
    """
    Return a HTTP 303 response, effectively redirecting
    the client to the given URL in a Post/Redirect/Get manor.

    Arguments:
        url:    Absolute URL within pyroTorrent.
                Should therefore include preceding slash.
                URL should not include base URL.

                Example: '/' For the main page.

    Returns: tuple containing pyroTorrent custom request.
    """

    # Since the pyroTorrentApp parses tuples as custom
    # responses, return a tuple containing the required info.
    # A 303 should not result in resubmission of POST data
    # to the given location.
    return ('303 See Other', [('Location', BASE_URL + url)], '')

def redirect_client(url):
    """
    Return a HTTP 307 response, effectively redirecting
    the client to the given URL.

    Arguments:
        url:    Absolute URL within pyroTorrent.
                Should therefore include preceding slash.
                URL should not include base URL.

                Example: '/' For the main page.

    Returns: tuple containing pyroTorrent custom request.
    """

    # Since the pyroTorrentApp parses tuples as custom
    # responses, return a tuple containing the required info
    # A 307 should not be cached unless explicitely stated so
    # by the HTTP headers.
    return ('307 Temporary Redirect', [('Location', BASE_URL + url)], '')

