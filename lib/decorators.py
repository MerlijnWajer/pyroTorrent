"""
pyroTorrent decorators - providing validation and lookup routines
"""

# 'inspect' is used for function standards validation.
import inspect

from functools import wraps

# pyro's web framework
from flask import session, g, abort

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

# Basic lookup method, wrapping all pyroTorrent views.
def pyroview(func = None, require_login = True, do_lookup_user = False):
    """
    pyroTorrent - standard view wrapper

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
        g.user = Result of lookup_user operation.
    """

    # All hail closures

    ################################
    ### Optional arguments hack  ###
    ################################
    def owhy(func):

        ################################
        ### Actual wrapping function ###
        ################################
        # Use wraps here since we skip the decorator module
        # in this function.
        @wraps(func)
        def pyroview_func(*args, **key_args):
            """
            pyroview internal function wrapper
            """

            print "pyroview_func"
            print args, key_args

            # Force a login if necessary
            if require_login:
                if not loggedin_and_require():
                    # If you wonder why the definition of the
                    # following function is nowhere to be found, check
                    # '/pyrotorrent.py'.
                    return handle_login()

            # Lookup user
            try:
                user_name = session['user_name']
                user = lookup_user(user_name)
            except KeyError, e:
                user = None
            g.user = user

            # Pass argument if requested
            if do_lookup_user:
                key_args['user'] = user

            return func(*args, **key_args)

        # FIXME: pyroview does not preserve signature to fix
        #some unexpected decorator behaviour
        #return decorator(pyroview_func, func)
        return pyroview_func

    # pyroview was called using '@pyroview'
    if func:
        return owhy(func)

    # pyroview was called using '@pyroview(...)'
    # I would say this is a weakness in the PEP318 spec, but
    # there is proabably a reason for this..
    # It makes decorators taking optional arguments a pain to
    # implement.
    # http://www.python.org/dev/peps/pep-0318/
    return owhy

def require_target(func):
    """
    Wrap a function requiring a target client. Implements
    automatic rejection semantics to ensure user authorisation.

    provides:
        target argument
    """

    # Validate target argument
    #if 'target' not in inspect.getargspec(func)[0]:
    #    raise AppStandardsViolation('require_target', func, [(-1, 'target')])

    ################################
    ### Actual wrapping function ###
    ################################
    #def target_func(func, target, *args, **key_args):
    @wraps(func)
    def target_func(target, *args, **key_args):
        """
        require_target internal target argument wrapper.
        """

        print "target_func"
        print key_args

        # Perform target lookup for callback function
        target = lookup_target(target)

        # Return 404 on target not found
        if target is None:
            return abort(404)

        # Reject user if not allowed to view this target
        if USE_AUTH:
            if g.user == None or target['name'] not in g.user.targets:
                return abort(404) # 404

        print target, args, key_args
        return func(target = target, *args, **key_args)

    #return decorator(target_func, func)
    return target_func

def require_torrent(func):
    """
    Wrap a function working on a specific torrent.
    This decorator expects Flask to pass a 'torrent_hash' argument.

    converts:
        torrent_hash into a torrent object.
    provides:
        torrent argument.
    """

    print '@require_torrent'
    # Validate torrent argument
    #if 'torrent' not in inspect.getargspec(func)[0]:
    #    raise AppStandardsViolation('require_torrent', func, [(-1, 'torrent')])

    ################################
    ### Actual wrapping function ###
    ################################
    #def torrent_func(func, target, torrent, *args, **key_args):
    @wraps(func)
    def torrent_func(target, *args, **key_args):
        """
        require_torrent internal torrent argument wrapper
        """

        print "torrent_func"
        print key_args

        # Grab torrent_hash
        if not key_args.has_key('torrent'):
            bugstr = "!!! BUG: route is not passing a 'torrent' " + \
                "argument like it should"
            print bugstr
            raise AppBugException(bugstr)

        # Build torrent object
        torrent_hash = key_args['torrent']
        t = Torrent(target, torrent_hash)

        # torrent_hash is contained by torrent object and thus superfluous
        #del key_args['torrent_hash']
        key_args['torrent'] = t
        print key_args

        return func(target = target, *args, **key_args)

    #return decorator(torrent_func, func)
    return torrent_func

def require_rtorrent(func):
    """
    Wrap a function requiring an RTorrent object.

    expects:
        target argument
    provides:
        rtorrent argument
    """

    ## Validate torrent argument
    #if 'rtorrent' not in inspect.getargspec(func)[0]:
    #    raise AppStandardsViolation('require_rtorrent', func, [(-1, 'rtorrent')])

    ################################
    ### Actual wrapping function ###
    ################################
    #def rtorrent_func(func, *args, **key_args):
    @wraps(func)
    def rtorrent_func(*args, **key_args):
        """
        require_rtorrent internal torrent argument wrapper
        """

        # Setup torrent object.
        r = RTorrent(key_args['target'])
        key_args['rtorrent'] = r

        return func(*args, **key_args)

    #return decorator(rtorrent_func, func)
    return rtorrent_func

