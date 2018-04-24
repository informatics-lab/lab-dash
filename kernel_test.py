import jupyter_client
from threading import Thread
import time

multi_km = jupyter_client.MultiKernelManager()
kid = 'mykernel'
multi_km.start_kernel(kernel_id=kid)
km = multi_km.get_kernel(kid)
km.client_class = 'jupyter_client.client.KernelClient'
try:
    kc = km.client()
    kc.start_channels()
    iopub = kc.iopub_channel
except AttributeError:
    # IPython 0.13
    kc = km
    kc.start_channels()
    iopub = kc.sub_channel
shell = kc.shell_channel

def get_io_messages():
    while True:
        msg = iopub.get_msg()
        print(msg['msg_type'])


# code = """import ipywidgets as widgets
# widgets.IntSlider()"""

# code = """print('hi')"""


# tio = Thread(target=get_io_messages)
# tio.start()

# kc.execute(code)

# time.sleep(10)%