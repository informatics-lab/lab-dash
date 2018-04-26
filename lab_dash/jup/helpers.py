import nbformat
import os

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__),'..','assets')
NOTEBOOK_DIR = os.path.abspath(os.path.join(os.curdir, 'notebooks')) # TODO: get this a better way?

def safe_notebook_path(path):
    path = os.path.normpath(os.path.join(NOTEBOOK_DIR, path))
    assert os.path.commonpath([NOTEBOOK_DIR, path]) == NOTEBOOK_DIR
    return path

def get_code(path, cell_number):
    path = safe_notebook_path(path)
    code = nbformat.read(open(path), 4)['cells'][cell_number]['source']

    return code