from notebook.services.kernelspecs.handlers import KernelSpecHandler, kernel_name_regex, MainKernelSpecHandler
default_handlers = [
    (r"/api/kernelspecs", MainKernelSpecHandler),
    (r"/api/kernelspecs/%s" % kernel_name_regex, KernelSpecHandler)
]