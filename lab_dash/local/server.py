"""
An example demonstrating a stand-alone "notebook".

Copyright (c) Jupyter Development Team.
Distributed under the terms of the Modified BSD License.

Example
-------

To run the example, see the instructions in the README to build it. Then
run ``python main.py``.

"""
import os
from jinja2 import FileSystemLoader
from notebook.base.handlers import IPythonHandler, FileFindHandler
from notebook.notebookapp import NotebookApp
from traitlets import Unicode
import logging
from tornado import web, ioloop
from threading import Thread
from .api_handelers import APIHandeler
from .security import RandomCodeBlocker
from . import config
logger = logging.getLogger("pangeo-dashboarding-proxy")


# def start_notbook_server():
#     nbApp = NotebookApp()
#     nbApp.open_browser = False
#     nbApp.port_retries = 0
#     nbApp.port = 8888
#     nbApp.initialize()
#     nbApp.start()


TEMPLATE_DIR = os.path.join(os.path.dirname(__file__),'..','assets')

class HomeHandler(web.RequestHandler):
    """Handle requests between the main app page and notebook server."""

    def get(self):
        """Get the main page for the application's interface."""
        logger.info('get main page')
        return self.render(os.path.join(TEMPLATE_DIR, 'index.html'),
            static='', base_url=config.BASE_URL, notebook=config.NOTEBOOK,
            token='none')



def main():

    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    logger.info('Started')

    # ioloop.IOLoop.current().run_in_executor(executor=None, func=start_notbook_server)
    build_dir =  os.path.join(os.path.dirname(__file__), '..', '..' ,'build')
    logger.info('build dir is %s', build_dir)
    application = web.Application([
        (r'/?', HomeHandler),
        (r"/api/(.*)", APIHandeler),
        (r'/(.*)', web.StaticFileHandler, {'path':build_dir}),
        (r'/api2/)
    ])
    port = 7777
    application.listen(port)
    logger.info('Running at http://localhost:{port}'.format(port=port))
    ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
