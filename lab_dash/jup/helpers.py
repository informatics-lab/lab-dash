import nbformat
def get_code(path, cell_number):
    # TODO: safety check 'path' since this is user supplied. Make sure no '../' or '*' or similar
    code = nbformat.read(open('notebooks/test.ipynb'), 4)['cells'][cell_number]['source']

    return code