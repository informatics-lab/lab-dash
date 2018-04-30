from notebook.services.kernels.handlers import MainKernelHandler, KernelHandler, KernelActionHandler, ZMQChannelsHandler, _kernel_id_regex, _kernel_action_regex
from .logging_mixin import Logging
import json
from notebook.base.zmqhandlers import deserialize_binary_message
from .. import helpers
from tornado import gen, web
from notebook.utils import url_path_join, url_escape
from jupyter_client.jsonutil import date_default

class KernelRegistry(object):
    def __init__(self):
        self.reg = {}

    def add(self,kernel_id, notebook=None):
        self.reg[kernel_id] = {'notebook':notebook}
    
    def get_notebook(self,kernel_id):
        return self.reg.get(kernel_id, {'notebook':None})['notebook']

    def set_notbook(self, kernel_id, notebook):
        details = self.reg[kernel_id]
        assert details['notebook'] == None or  details['notebook'] == notebook
        details['notebook'] = notebook


kernel_reg = KernelRegistry() # TODO: is module level the right place for this?

class MainKernelFixToNotebookHandler(MainKernelHandler):
    
    @web.authenticated
    @gen.coroutine
    def get(self):
        # TODO: only return kernels for the current user/session.
        km = self.kernel_manager
        kernels = yield gen.maybe_future(km.list_kernels())
        self.finish(json.dumps(kernels, default=date_default))

    @web.authenticated
    @gen.coroutine
    def post(self):
        """Most of this is taken from the super class MainKernelHandler but we hijack the name field to specify the notebook we want to run"""
        km = self.kernel_manager
        model = self.get_json_body()
        if model is None:
            msg = "Must supply a body with a name formated like {\"name\":\<path_to_notebook>}"
            raise web.HTTPError(400,msg,reason=msg)
  
        name = json.loads(model.get('name',''))
        notebook = None
        if isinstance(name, dict):
            notebook = name.get('notebook', None)
        if notebook == None:
            msg = "Must supply a body with a name formated like {\"name\":\<path_to_notebook>}"
            raise web.HTTPError(400,msg,reason=msg)
        del model['name']
            
        model.setdefault('name', km.default_kernel_name)

        kernel_id = yield gen.maybe_future(km.start_kernel(kernel_name=model['name']))
        model = km.kernel_model(kernel_id)
        location = url_path_join(self.base_url, 'api', 'kernels', url_escape(kernel_id))


        kernel_reg.add(kernel_id, notebook)
        self.set_header('Location', location)
        self.set_status(201)
        self.finish(json.dumps(model, default=date_default))


class ChannelsHandler(ZMQChannelsHandler, Logging):
    def on_message(self, msg):
        self.logger.info(msg)

        if isinstance(msg, bytes):
            msg_obj = deserialize_binary_message(msg)
        else:
            msg_obj = json.loads(msg)

        if(msg_obj['header']['msg_type'] == 'execute_request'):
            return # Ignore 'request_execute' TODO: other things to ignore?

        if(msg_obj['header']['msg_type'] == 'run_cell'):
            self.logger.info('RUN a CELL!!!')
            cell_number = msg_obj['content']['cell_number']
            code = helpers.get_code(kernel_reg.get_notebook(self.kernel_id), cell_number)
            msg_obj['header']['msg_type'] = 'execute_request'
            msg_obj['content'] = {
                "silent":False,
                "store_history":True,
                "user_expressions":{},
                "allow_stdin":True,
                "stop_on_error":True,
                "code":code
            }
            msg = json.dumps(msg_obj)

            self.logger.info('**NEW MESSAGE**: %s' % msg)
        
        super().on_message(msg)

        
default_handlers = [
    (r"/api/kernels", MainKernelFixToNotebookHandler),
    (r"/api/kernels/%s" % _kernel_id_regex, KernelHandler),
    (r"/api/kernels/%s/%s" % (_kernel_id_regex, _kernel_action_regex), KernelActionHandler),
    (r"/api/kernels/%s/channels" % _kernel_id_regex, ChannelsHandler)
]