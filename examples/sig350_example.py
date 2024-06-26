from mtcadapter.adapters import MTCAdapter
from mtcadapter.mtcdevices.sick import SIG350, SICK_IMC30_Sensor, SICK_AHS_AHM36_Sensor

"""
Example to demonstrate the usage of SIG350 with two sensors connected to it

For this example, the environment variable `SIG350_IP` must be set
and a IMC30 and AHS/AHM36 sensor connected to the SIG350

"""


class MySIG350(SIG350):
    sensors = {'master1port4': SICK_IMC30_Sensor,
               'master1port8': SICK_AHS_AHM36_Sensor}


class MyAdapter(MTCAdapter):
    adapter_port = 7878
    device_class = MySIG350


def main():
    myadapter = MyAdapter()
    myadapter.run()


if __name__ == "__main__":
    main()
