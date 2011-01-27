import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from pyrotorrent.lib.base import BaseController, render
from pyrotorrent.model.rtorrent import RTorrent

log = logging.getLogger(__name__)

class PyroController(BaseController):

    def index(self):
        # Return a rendered template
        #return render('/pyro.mako')
        # or, return a string

        r = RTorrent('sheeva')

        c.download_titles = r.get_download_list()

        return render('/download_list.jinja2')
        return 'Welcome to pyroTorrent'
