from notebook.services.sessions.handlers import _session_id_regex , SessionHandler #, SessionRootHandler 
import json
from tornado import web
from .logging_mixin import Logging
import nbformat

class SessionRootHandler(web.RequestHandler, Logging):
    """Handle requests between the main app page and notebook server."""

    def get(self):
        self.set_header("Content-Type", "application/json")
        output = json.dumps([])
        return self.write(output)



default_handlers = [
    # (r"/api/sessions/%s" % _session_id_regex, SessionHandler),
    (r"/api/sessions",  SessionRootHandler)
]