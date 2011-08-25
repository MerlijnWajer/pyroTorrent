"""
pyroTorrent decorators - providing validation and lookup routines
"""

# Inspect is used for function standards validation
import inspect

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

# Basic lookup method, wrapping all pyroTorrent methods
# called by webtool
def webtool_callback(func, require_login = True, lookup_user = False):
    """
    lib.webtool - standard interface wrapper

    require_login:
        When enabled, page will reject users without authorisation.
    """

    # Validate env argument
    if inspect.getargspect(func)[0][0] != 'env':
        raise AppSemanticException('webtool_callback', func, [(0, 'env')])

    # All hail closures
    def webtool_func(*args, **key_args):
        func(*args, **key_args)

    return webtool_func

def require_torrent_requester(func):

