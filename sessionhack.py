import traceback
import sys

class SessionHackException(Exception):
    """
    Raised when something goes wrong.
    """

class SessionHack(object):
    """
        The SessionHack middleware is used to catch any exceptions that occur;
        this makes debugging easier. Typically debugging can be painful because
        the trace and error is only shown in the web page.
    """

    def __init__(self, app):
        self.app = app

    def __call__(self, env, start_response):
        try:
            ret = self.app(env, start_response)
        except Exception, e:
            print 'Exception in SessionHack:', e.message
            print '-' * 60
            traceback.print_exc(file=sys.stdout)
            print '-' * 60
            raise SessionHackException(e.message)
        finally:
            pass

        return ret
