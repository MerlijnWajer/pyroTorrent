import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from pyrotorrent.lib.base import BaseController, render

log = logging.getLogger(__name__)

class PyroController(BaseController):

    def index(self):
        # Return a rendered template
        #return render('/pyro.mako')
        # or, return a string
        return 'Welcome to pyroTorrent'
