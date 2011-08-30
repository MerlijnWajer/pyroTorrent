"""
pyroTorrent decorators - providing validation and lookup routines
"""

# Inspect is used for function standards validation
import inspect

# pyro imports
from config import USE_AUTH

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
    def __init__(dec, func, args):
        self.py_file = inspect.getsourcefile(func)
        self.py_line = inspect.getsourcelines(func)[1]
        self.py_name = func.__name__
        self.args = args
        self.dec = dec

        arg_error = ''

        for arg in args:
            if arg[0] == -1:
                arg_error += "\n    missing argument '%s'" arg[1]
            else:
                arg_error += "\n    argument %i, expecting '%s'" % arg
        Exception.__init__(self,
            '%s:%s: @%s: Function '%s' breaks application semantics%s' %
            (self.py_file, self.py_line, dec, self.py_name, arg_error))

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

####################################################
####################################### # # ########
# From here on decorators only! ######## # # #######
####################################### # # ########
####################################################

# Basic lookup method, wrapping all pyroTorrent methods
# called by webtool
def webtool_callback(func, require_login = True, lookup_user = False):
    """
    lib.webtool - standard interface wrapper

    require_login:
        When enabled, page will reject users without authorisation.
        Opposingly disabling will render the page without problems.
    lookup_user:
        When enabled, decorator will lookup the current user, and
        provide it as an additional argument.
    """

    # Validate env argument
    if inspect.getargspect(func)[0][0] != 'env':
        raise AppSemanticException('webtool_callback', func, [(0, 'env')])

    # XXX: When wrapping a require_target, we need to force user lookup
    # since this decorator expects it, throw a warning if lookup_user
    # is set to false

    # TODO: Implement that ^

    # All hail closures

    ################################
    ### Actual wrapping function ###
    ################################
    def webtool_func(env, *args, **key_args):
        if require_login:
            if not loggedin_and_require(env):
                return handle_login(env)

        if lookup_user:
        return func(env, *args, **key_args)

    return webtool_func

def require_target(func):
    """
    Wrap a function requiring a target client. Implements
    automatic rejection semantics to ensure user authorisation.
    """

    # Validate target argument
    if inspect.getargspect(func)[0][1] != 'target':
        raise AppStandardsException('require_target', func, [(1, 'env')])

    ################################
    ### Actual wrapping function ###
    ################################
    def target_func(env, target, *args, **key_args):
        # Perform target lookup for callback function
        target = lookup_target(target)

        # Return 404 on target not found
        if target is None:
            return None # 404

        # Reject user if not allowed to view this target
        if USE_AUTH:
            if user == None or target['name'] not in user.targets:
                return None # 404

        return func(env, target, *arg, **keys)

    return target_func

def require_torrent(func):

def require_torrent_requester(func):

