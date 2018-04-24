import jupyter_client
from tornado import web, ioloop
import logging
import json
import nbformat
from .websockets import WebSocketHandlerMixin

import builtins
# A stray _ in the notebook.services.contents.manager causes an error without this.
builtins._ = lambda x: x
from notebook.services.contents.filemanager import FileContentsManager

logger = logging.getLogger("pangeo-dashboard-server")

k_spec_manager = jupyter_client.kernelspec.KernelSpecManager()
k_manager = jupyter_client.MultiKernelManager()

filemanager = FileContentsManager()

from datetime import date, datetime


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()


class JSONHandeler(web.RequestHandler):
    def set_default_headers(self, *args, **kwargs):
        return self.set_header('Content-Type', 'application/json')

    def write_json(self, obj):
        return self.write(json.dumps(obj, default=json_serial))


class KernelHandeler(WebSocketHandlerMixin, JSONHandeler):
    """Handle requests between the main app page and notebook server."""

    async def http_get(self, api):
        """Get the main page for the application's interface."""
        logger.info('%s: get api %s', self.__class__, api)
        # TODO not hard code default kernal
        default = 'python3'
        kernels = {
            "default": default,
            "kernelspecs": {
                default: {
                    "name": "python3",
                    "resources": {
                        "logo-32x32": "/kernelspecs/python3/logo-32x32.png",
                        "logo-64x64": "/kernelspecs/python3/logo-64x64.png"
                    },
                    "spec": k_spec_manager.get_all_specs()['python3']['spec']
                }}}

        self.write_json(kernels)

        
    def open(self, api):
        """
        Called when a client opens a websocket connection.
        We establish a websocket connection to the proxied backend &
        set up a callback to relay messages through.
        """
        logger.info('open ws, %s', api)


        # if self.request.query:
        #     client_uri += '?' + self.request.query

        def cb(message):
            """
            Callback when the backend sends messages to us
            We just pass it back to the frontend
            """
            # Websockets support both string (utf-8) and binary data, so let's
            # make sure we signal that appropriately when proxying
            if message is None:
                self.close()
            else:
                self.write_message(message, binary=type(message) is bytes)

        async def start_websocket_connection():
            cb("""{"header":{"version":"5.3","date":"2018-03-23T12:20:35.401498Z","session":"6865dfce-12d72962472b5c40b22b6232","username":"theo","msg_type":"kernel_info_reply","msg_id":"2e361eb5-6a6f254c901285fcba38161d"},"msg_id":"2e361eb5-6a6f254c901285fcba38161d","msg_type":"kernel_info_reply","parent_header":{"username":"","version":"5.2","session":"0b99dbedcc34850390ec2e237cc27590","msg_id":"354e037abf802a3edbcf814013aef1f0","msg_type":"kernel_info_request","date":"2018-03-23T12:20:35.398951Z"},"metadata":{},"content":{"status":"ok","protocol_version":"5.1","implementation":"ipython","implementation_version":"6.2.1","language_info":{"name":"python","version":"3.6.4","mimetype":"text/x-python","codemirror_mode":{"name":"ipython","version":3},"pygments_lexer":"ipython3","nbconvert_exporter":"python","file_extension":".py"},"banner":"Python 3.6.4 |Anaconda, Inc.| (default, Mar 12 2018, 20:05:31) \nType 'copyright', 'credits' or 'license' for more information\nIPython 6.2.1 -- An enhanced Interactive Python. Type '?' for help.\n","help_links":[{"text":"Python Reference","url":"https://docs.python.org/3.6"},{"text":"IPython Reference","url":"https://ipython.org/documentation.html"},{"text":"NumPy Reference","url":"https://docs.scipy.org/doc/numpy/reference/"},{"text":"SciPy Reference","url":"https://docs.scipy.org/doc/scipy/reference/"},{"text":"Matplotlib Reference","url":"https://matplotlib.org/contents.html"},{"text":"SymPy Reference","url":"http://docs.sympy.org/latest/index.html"},{"text":"pandas Reference","url":"https://pandas.pydata.org/pandas-docs/stable/"}]},"buffers":[],"channel":"shell"}""")

        ioloop.IOLoop.current().add_callback(start_websocket_connection)

    def on_message(self, message):
        """
        Called when we receive a message from our client.
        We proxy it to the backend.
        """
        logger.info('have message %s', message)
        if hasattr(self, 'ws'):
            self.ws.write_message(message)

    def on_close(self):
        """
        Called when the client closes our websocket connection.
        We close our connection to the backend too.
        """
        logger.info('close')
        if hasattr(self, 'ws'):
            self.ws.close()



class ContentHandeler(JSONHandeler):
    def get(self, file):
        """Get the main page for the application's interface."""
        logger.info('%s: get api %s', self.__class__, file)
        if(file.split('/')[-1] == 'checkpoints'):
            return self.write_json([{"id": "checkpoint", "last_modified": datetime.now()}])
        else:
            return self.write_json(filemanager.get(file))

    def post(self, file):
        """Get the main page for the application's interface."""
        logger.info('%s: get api %s', self.__class__, file)
        if(file.split('/')[-1] != 'checkpoints'):
            raise web.HTTPError(405)
        else:
            return self.write_json(filemanager.get(file))


class SessionHandeler(JSONHandeler):
    """Handle requests between the main app page and notebook server."""

    def get(self, api):
        """Get the main page for the application's interface."""
        logger.info('%s: get api %s', self.__class__, api)
        return self.write_json([])

    def post(self, api):
        """Get the main page for the application's interface."""
        logger.info('%s: get api %s', self.__class__, api)
        s_type = json.loads(self.request.body)
        # TODO, Some checking that this is the type of session we want.
        kernal_id = k_manager.start_kernel(s_type["kernel"]["name"])
        resp = {
            "id": kernal_id,
            "path": s_type['path'],
            "name": s_type['name'],
            "type": s_type['type'],
            "kernel": {
                "id": kernal_id,
                "name": "python3",
                # "last_activity": "2018-03-23T09:25:40.516129Z",
                "execution_state": "starting",
                "connections": 0
            },
            "notebook": {
                "path": s_type['path'],
                "name": s_type['name']
            }
        }

        self.set_status(201)
        return self.write_json(resp)


    