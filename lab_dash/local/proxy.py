"""
With thanks to and based on
nbserverproxy
https://github.com/jupyterhub/nbserverproxy/blob/master/nbserverproxy/handlers.py

"""
import inspect
import socket
import json
import os
from tornado import gen, web, httpclient, httputil, process, websocket, ioloop
import pprint
import logging
from .security import RandomCodeBlocker
from . import config

logger = logging.getLogger("pangeo-dashboarding-proxy")
pp = pprint.PrettyPrinter(indent=4)


# {"header":{"username":"","version":"5.2","session":"3facd31dd5be2e84fd2503da40844e64","msg_id":"402df1a39b9c6fcb7d3f5f1d95956da5","msg_type":"execute_request"},"parent_header":{},"channel":"shell","content":{"silent":false,"store_history":true,"user_expressions":{},"allow_stdin":true,"stop_on_error":true,"code":"from bokeh.io import push_notebook, show, output_notebook\nfrom bokeh.layouts import row\nfrom bokeh.plotting import figure\noutput_notebook()"},"metadata":{},"buffers":[]}



# TODO: sort out this whole mess of when and how the callback and blocker all wired together. Yuck.
codeBlocker = RandomCodeBlocker(config.NOTEBOOK_DIR + '/' + config.NOTEBOOK) if  config.NOTEBOOK else None

def on_message_in(mess, proxy):
    message = json.loads(mess)
    # with open('ws.log','a') as log:
    #     log.write(pp.pformat(message))
    #     log.write('\n\n')
    logger.info("WS in -  channel:%s, type:%s", message['channel'], message['header']['msg_type'])

    if message['channel'] == 'shell' and message['header']['msg_type'] == "execute_request":
        if codeBlocker and not codeBlocker.is_allowed(message['content']['code']):
            logger.info('block: \n%s ',message['content']['code']) 
            return
    proxy.ws.write_message(mess)

# from https://stackoverflow.com/questions/38663666/how-can-i-serve-a-http-page-and-a-websocket-on-the-same-url-in-tornado
class WebSocketHandlerMixin(websocket.WebSocketHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # since my parent doesn't keep calling the super() constructor,
        # I need to do it myself
        bases = inspect.getmro(type(self))
        assert WebSocketHandlerMixin in bases
        meindex = bases.index(WebSocketHandlerMixin)
        try:
            nextparent = bases[meindex + 1]
        except IndexError:
            raise Exception("WebSocketHandlerMixin should be followed "
                            "by another parent to make sense")

        # undisallow methods --- t.ws.WebSocketHandler disallows methods,
        # we need to re-enable these methods
        def wrapper(method):
            def undisallow(*args2, **kwargs2):
                getattr(nextparent, method)(self, *args2, **kwargs2)
            return undisallow

        for method in ["write", "redirect", "set_header", "set_cookie",
                       "set_status", "flush", "finish"]:
            setattr(self, method, wrapper(method))
        nextparent.__init__(self, *args, **kwargs)

    async def get(self, *args, **kwargs):
        if self.request.headers.get("Upgrade", "").lower() != 'websocket':
            return await self.http_get(*args, **kwargs)
        # super get is not async
        super().get(*args, **kwargs)


class LocalProxyHandler(WebSocketHandlerMixin, web.RequestHandler):
    
    def __init__(self, *args, proxy_to_port=8888, prefix='', **kwargs):
        super().__init__(*args, **kwargs)
        self.proxy_to_port = proxy_to_port
        self.prefix = prefix

    def open(self, proxied_path=''):
        """
        Called when a client opens a websocket connection.
        We establish a websocket connection to the proxied backend &
        set up a callback to relay messages through.
        """
        if not proxied_path.startswith('/'):
            proxied_path = '/' + proxied_path

        client_uri =  'ws://localhost:{port}{prefix}{path}'.format(
            port=self.proxy_to_port,
            prefix=self.prefix,
            path=proxied_path
        )

        if self.request.query:
            client_uri += '?' + self.request.query

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
            logger.info('Trying to establish websocket connection to %s', client_uri)
            self.ws = await websocket.websocket_connect(client_uri, on_message_callback=cb)
            logger.info('Websocket connection established to %s', client_uri)

        ioloop.IOLoop.current().add_callback(start_websocket_connection)

    def on_message(self, message):
        """
        Called when we receive a message from our client.
        We proxy it to the backend.
        """
        if hasattr(self, 'ws'):
            on_message_in(message, self)

    def on_close(self):
        """
        Called when the client closes our websocket connection.
        We close our connection to the backend too.
        """
        if hasattr(self, 'ws'):
            self.ws.close()

    async def proxy(self, proxied_path):
        '''
        Proxy everything.
        '''
        # logger.info('Proxy %s:%s' % ( self.request.method, proxied_path))

        if not proxied_path.startswith('/'):
            proxied_path = '/' + proxied_path

        if 'Proxy-Connection' in self.request.headers:
            del self.request.headers['Proxy-Connection']

        body = self.request.body
        if not body:
            if self.request.method == 'POST':
                body = b''
            else:
                body = None

        
        client_uri = 'http://localhost:{port}{prefix}{path}'.format(
            port=self.proxy_to_port,
            prefix=self.prefix,
            path=proxied_path
        )
        if self.request.query:
            client_uri += '?' + self.request.query

        client = httpclient.AsyncHTTPClient()
        # client = httpclient.HTTPClient()

        
        req = httpclient.HTTPRequest(
            client_uri, method=self.request.method, body=body,
            headers=self.request.headers, follow_redirects=False)

        # logger.info('Will call %s %s. Headers: %s' % (req.method, req.url, list(req.headers.get_all()) ))
        response = await client.fetch(req, raise_error=False) 

        # For all non http errors...
        if response.error and type(response.error) is not httpclient.HTTPError:
            logger.error("proxyed request error:\n%s" % response)
            self.set_status(500)
            self.write(str(response.error))
        else:
            self.set_status(response.code, response.reason)

            # clear tornado default header
            self._headers = httputil.HTTPHeaders()

            for header, v in response.headers.get_all():
                if header not in ('Content-Length', 'Transfer-Encoding',
                    'Content-Encoding', 'Connection'):
                    # some header appear multiple times, eg 'Set-Cookie'
                    self.add_header(header, v)


            if response.body:
                self.write(response.body)

    # support all the methods that torando does by default!
    async def http_get(self, proxy_path=''):
        return await self.proxy( proxy_path)

    def post(self, proxy_path=''):
        return self.proxy(proxy_path)

    def put(self, proxy_path=''):
        return self.proxy(proxy_path)

    def delete(self, proxy_path=''):
        return self.proxy( proxy_path)

    def head(self, proxy_path=''):
        return self.proxy( proxy_path)

    def patch(self, proxy_path=''):
        return self.proxy(proxy_path)

    def options(self, proxy_path=''):
        return self.proxy(proxy_path)

    def check_xsrf_cookie(self):
        '''
        http://www.tornadoweb.org/en/stable/guide/security.html
        Defer to proxied apps.
        '''
        pass


