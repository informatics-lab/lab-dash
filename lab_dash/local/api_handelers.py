from .proxy import LocalProxyHandler

class APIHandeler(LocalProxyHandler):
    def __init__(self, *args, **kwargs):
        kwargs['prefix'] = '/api'
        super().__init__(*args, **kwargs)
        