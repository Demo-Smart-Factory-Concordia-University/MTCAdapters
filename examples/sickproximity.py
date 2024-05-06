from mtcadapter.adapters import MTCAdapter, AgentRequestHandler
from mtcadapter.mtcdevices.sick import SICKProximitySensor

"""
For this example, the environment variables
 - SIG350_IP
 - DEVICE_ALIAS
must be set
"""


class MySIG350Handler(AgentRequestHandler):
    device_class = SICKProximitySensor


class MyAdapter(MTCAdapter):
    agentRequestHandler_class = MySIG350Handler
    adapter_port = 7878


def main():
    myadapter = MyAdapter()
    myadapter.run()


if __name__ == "__main__":
    main()
