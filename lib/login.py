"""
De login heeft een paar kanten:
    -   De app moet bepaalde filters toepassen. Een user mag alleen maar bij
    bepaalde targets. (of views?)
    -   Er moet login validatie gedaan worden.
    -   Een deel moet ge-export worden naar jinja.

"""

class LoginManager(object):

    def __init__(self, app):
        self.app = app

    def __call__(self, env, start_response):
        # use beaker, do stuff
        session = env['beaker.session']

        return self.app(env, start_response)

def verify_target(env, target):
    session = env['beaker.session']

    return target['name'] in session['loginmanager']['targets']
