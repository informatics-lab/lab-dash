
# from jinja2 import FileSystemLoader
# from notebook.base.handlers import IPythonHandler, FileFindHandler
import logging
from tornado import web, ioloop
from notebook.services.kernels.kernelmanager import MappingKernelManager
import os
from jupyter_client.kernelspec import KernelSpecManager
from .handlers import pages_handler, kernels_handler, kernelspecs_handler, content_handeler

logger = logging.getLogger("lab_dash")


settings = dict(
    kernel_manager=MappingKernelManager(),
    kernel_spec_manager=KernelSpecManager(),
    logger=logger
)

default_handlers = (pages_handler.default_handlers + 
                    kernels_handler.default_handlers + 
                    kernelspecs_handler.default_handlers + 
                    content_handeler.default_handlers)

static_handler = (r'/(.*)', web.StaticFileHandler, {'path': os.path.join(os.path.dirname(__file__), '..', '..' ,'build')})
default_handlers += [static_handler]

def main():

    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    logger.info('Started')


    application = web.Application(default_handlers, **settings)
    port = 7777
    application.listen(port)
    logger.info('Running at http://localhost:{port}'.format(port=port))
    ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
