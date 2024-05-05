import psutil
from .mtcdevice import MTCDevice


class HardwareSensors(MTCDevice):

    def __init__(self):
        temps = psutil.sensors_temperatures()
        if not temps:
            raise Exception("Can't read any temperature on this machine")

    def read_data(self):
        data = {}
        temps = psutil.sensors_temperatures()
        for name, entries in temps.items():
            for entry in entries:
                data[entry.label or name] = entry.current
        return data
