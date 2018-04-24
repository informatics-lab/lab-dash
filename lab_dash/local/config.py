import os
NOTEBOOK = os.environ.get('NOTEBOOK', '')
NOTEBOOK_DIR = os.environ.get('NOTEBOOK_DIR', '')
BASE_URL = os.environ.get('PROXY_PREFIX','/')
BASE_URL = '/' + BASE_URL if BASE_URL[0] is not '/' else BASE_URL
BASE_URL = BASE_URL + '/' if BASE_URL[-1] is not '/' else BASE_URL