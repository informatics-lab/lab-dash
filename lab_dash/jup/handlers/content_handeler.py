import json
from jupyter_client.jsonutil import date_default
from tornado import web
from .logging_mixin import Logging
from .. import helpers
import nbformat

class ContentHandler(web.RequestHandler, Logging):
    """Handle requests between the main app page and notebook server."""

    def get(self, path):
        path = helpers.safe_notebook_path(path)
        nb = nbformat.read(open(path), 4)
        self.set_header("Content-Type", "application/json")
        output = json.dumps(nb, default=date_default)
        return self.write(output)



default_handlers = [ (r'/api/notebooks/(.*)', ContentHandler)]