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

    def __init__(self, app, render_call):
        self.app = app
        self.render_call = render_call

    def __call__(self, env, start_response):
        error = False
        try:
            ret = self.app(env, start_response)
        except Exception, e:
            print 'Exception in SessionHack:', e.message
            print '-' * 60
            traceback.print_exc(file=sys.stdout)
            print '-' * 60
            ret = self.render_call(env, str(e))
            #raise SessionHackException(e.message)
            error = True
        finally:
            pass

        if error:
            start_response('200 OK', [('Content-Type', 'text/html;charset=utf8')])
        return ret
