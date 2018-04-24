import os
from tornado import web
from .logging_mixin import Logging
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__),'..','..','assets')


class HomeHandler(web.RequestHandler, Logging):
    """Handle requests between the main app page and notebook server."""

    def get(self):
        """Get the main page for the application's interface."""
        self.logger.info('get main page')
        return self.render(os.path.join(TEMPLATE_DIR, 'index.html'),
            static='', base_url='/', notebook='',
            token='none')

default_handlers = [ (r'/?', HomeHandler)]