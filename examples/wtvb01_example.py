from mtcadapter.adapters import MTCAdapter
from mtcadapter.mtcdevices.witmotion import WTVB01


"""
Example for the WTVB01-485 vibration sensor from WitMotion
"""


class MyWTVB01(WTVB01):
    port = '/dev/ttyUSB0'
    temperature_id = None  # it will not return the temperature


class MyAdapter(MTCAdapter):
    adapter_port = 7878
    device_class = MyWTVB01


def main():
    myadapter = MyAdapter()
    myadapter.run()


if __name__ == "__main__":
    main()
