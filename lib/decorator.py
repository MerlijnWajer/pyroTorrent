"""
pyroTorrent decorators - providing validation and lookup routines
"""

# NOTE: Here are some details regarding global implementation
# and behaviour of the decorators.
"""
Functions returned by the decorator system will have an extra '_PYRO_deep_func'
member. This member will contain the original undecorated function and
can thus be used by any decorator to immediately access the decorated function
for various details.

Thus:
    @a
    @b
    c

will result in a function 'c' with c._PYRO_deep_func set to the
original value of 'c'.
"""


# Inspect is used for function standards validation
import inspect

# pyro imports
from config import USE_AUTH
from lib.helper import lookup_user, lookup_target, \
    detach_deep_func, attach_deep_func, loggedin_and_require
from model.torrent import Torrent
from model.rtorrent import RTorrent

###################################
# This section contains decorator #
# helpers.                        #
###################################

class AppStandardsViolation(Exception):
    """
    Function breaks application conventions

    dec:    Name of decorator that found the offending functions
    func:   Offending function
    args:   List of tuples, where each tuple is a pair of
            (arg_nr, arg_name)
                arg_nr: offending argument number
                arg_name: expected name
    """
    def __init__(self, dec, func, args):
        self.py_file = inspect.getsourcefile(func)
        self.py_line = inspect.getsourcelines(func)[1]
        self.py_name = func.__name__
        self.args = args
        self.dec = dec

        arg_error = ''

        for arg in args:
            if arg[0] == -1:
                arg_error += "\n    missing argument '%s'" % arg[1]
            else:
                arg_error += "\n    argument %i, expecting '%s'" % arg
        Exception.__init__(self,
            '%s:%s: @%s: Function \'%s\' breaks application semantics%s' %
            (self.py_file, self.py_line, dec, self.py_name, arg_error))

class AppBugException(Exception):
    """
    Thrown upon encountering a state that should not occur.
    """

####################################################
####################################### # # ########
# From here on decorators only! ######## # # #######
####################################### # # ########
####################################################

# Basic lookup method, wrapping all pyroTorrent methods
# The resulting function will be called by webtool
def webtool_callback(func = None, require_login = True, do_lookup_user = False):
    """
    lib.webtool - standard interface wrapper

    When calling this function without keyword arguments,
    you will want to keep the first argument None since this is a
    hack to make the function multisyntax compatible, see note at
    end of function code.

    require_login:
        When enabled, page will reject users without authorisation.
        Opposingly disabling will render the page without problems.
    lookup_user:
        When enabled, decorator will lookup the current user, and
        provide it as an additional argument.

    provides the following variables:
        evn['verified_user'] = Result of lookup_user operation.
    """

    # All hail closures

    ################################
    ### Optional arguments hack  ###
    ################################
    def owhy(func):
        deep_func = detach_deep_func(func)

        # Validate env argument
        if inspect.getargspec(deep_func)[0][0] != 'env':
            raise AppSemanticException('webtool_callback', deep_func, [(0, 'env')])

        ################################
        ### Actual wrapping function ###
        ################################
        def webtool_func(env, *args, **key_args):
            """
            webtool internal function wrapper
            """

            # Force a login if necessary
            if require_login:
                if not loggedin_and_require(env):
                    # If you wonder why the definition of the
                    # following function is nowhere to be found, check
                    # '/pyrotorrent.py'.
                    return handle_login(env)

            # Lookup user
            try:
                user_name = env['beaker.session']['user_name']
                user = lookup_user(user_name)
            except KeyError, e:
                user = None
            env['verified_user'] = user

            # Pass argument if requested
            if do_lookup_user:
                key_args['user'] = user

            return func(env, *args, **key_args)

        return attach_deep_func(webtool_func, deep_func)

    # webtool_callback was called using '@webtool_callback'
    if func:
        return owhy(func)

    # webtool_callback was called using '@webtool_callback(...)'
    # I would say this is a weakness in the PEP318 spec, but
    # there is proabably a reason for this..
    # It makes decorators taking optional arguments a pain to # implement.
    # http://www.python.org/dev/peps/pep-0318/
    return owhy

def require_target(func):
    """
    Wrap a function requiring a target client. Implements
    automatic rejection semantics to ensure user authorisation.
    """

    deep_func = detach_deep_func(func)

    # Validate target argument
    if inspect.getargspec(deep_func)[0][1] != 'target':
        raise AppStandardsViolation('require_target', deep_func, [(1, 'env')])

    ################################
    ### Actual wrapping function ###
    ################################
    def target_func(env, target, *args, **key_args):
        """
        webtool internal target argument wrapper.
        """
        # Perform target lookup for callback function
        target = lookup_target(target)

        # Return 404 on target not found
        if target is None:
            return None # 404

        user = env['verified_user']

        # Reject user if not allowed to view this target
        if USE_AUTH:
            if user == None or target['name'] not in user.targets:
                return None # 404

        return func(env, target = target, *args, **key_args)

    return attach_deep_func(target_func, deep_func)

def require_torrent(func):
    """
    Wrap a function working on a specific torrent.
    This decorator expects webtool to pass a 'torrent_hash' argument.

    provides:
        env['torrent']
    """

    deep_func = detach_deep_func(func)

    # Validate torrent argument
    if 'torrent' not in inspect.getargspec(deep_func)[0]:
        raise AppStandardsViolation('require_torrent', deep_func, [(-1, 'torrent')])

    ################################
    ### Actual wrapping function ###
    ################################
    def torrent_func(env, target, *args, **key_args):
        """
        webtool internal torrent argument wrapper
        """

        # Grab torrent_hash
        if not key_args.has_key('torrent_hash'):
            bugstr = "!!! BUG: Webtool is not passing a 'torrent_hash' " + \
                "argument like it should"
            print bugstr
            raise AppBugException(bugstr)

        # Build torrent object
        torrent_hash = key_args['torrent_hash']
        t = Torrent(target, torrent_hash)

        # torrent_hash is contained by torrent object and thus superfluous
        del key_args['torrent_hash']
        key_args['torrent'] = t

        return func(env, target = target, *args, **key_args)

    return attach_deep_func(torrent_func, deep_func)

def require_rtorrent(func):
    """
    Wrap a function requiring an RTorrent object.
    """

    deep_func = detach_deep_func(func)

    # Validate torrent argument
    if 'rtorrent' not in inspect.getargspec(deep_func)[0]:
        raise AppStandardsViolation('require_rtorrent', deep_func, [(-1, 'rtorrent')])

    ################################
    ### Actual wrapping function ###
    ################################
    def rtorrent_func(env, *args, **key_args):
        """
        webtool internal torrent argument wrapper
        """

        # Setup torrent object.
        r = RTorrent(key_args['target'])
        key_args['rtorrent'] = r

        return func(env, *args, **key_args)

    return attach_deep_func(rtorrent_func, deep_func)

