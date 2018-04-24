import nbformat
class RandomCodeBlocker(object):
    def __init__(self, notebook):
        with open(notebook) as fp:
            nb = nbformat.read(fp, nbformat.NO_CONVERT)
        
        self.allowed_code = set()
        for cell in nb.cells:
            self.allowed_code.add(cell['source'])
    
    def is_allowed(self, code):
        return code in self.allowed_code

