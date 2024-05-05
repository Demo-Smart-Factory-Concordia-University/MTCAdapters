from mtcadapter.adapters import MTCAdapter, DeviceHandler
from mtcadapter.mtcdevices import HardwareSensors


class MyHardwareHandler(DeviceHandler):
    device_class = HardwareSensors


class MyAdapter(MTCAdapter):
    deviceHandler_class = MyHardwareHandler
    adapter_port = 7878


def main():
    myadapter = MyAdapter()
    myadapter.run()


if __name__ == "__main__":
    main()
