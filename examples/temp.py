from mtcadapter.adapters import MTCAdapter, AgentRequestHandler
from mtcadapter.mtcdevices import HardwareSensors


class MyHardwareHandler(AgentRequestHandler):
    device_class = HardwareSensors


class MyAdapter(MTCAdapter):
    agentRequestHandler_class = MyHardwareHandler
    adapter_port = 7878


def main():
    myadapter = MyAdapter()
    myadapter.run()


if __name__ == "__main__":
    main()
