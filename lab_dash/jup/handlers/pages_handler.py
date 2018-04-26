import os
from tornado import web
from .logging_mixin import Logging
from .. import helpers
import os

class HomeHandler(web.RequestHandler, Logging):
    """Handle requests between the main app page and notebook server."""

    def get(self):
        """Get the main page for the application's interface."""
        self.logger.info('get main page')
        return self.render(os.path.join(helpers.TEMPLATE_DIR, 'index.html'),
            static='', base_url='/', notebook='',
            token='none')

default_handlers = [ (r'/?', HomeHandler)]