import requests
import os
import time
from mtcadapter.mtcdevices import MTCDevice
from mtcadapter.exceptions import ImproperlyConfigured


"""
SICK SIG350 Sensor Integration Gateway
Uses the SIG350 REST API to read sensor data
"""


class SIG350(MTCDevice):

    ip_address = os.getenv('SIG350_IP') or None
    sensors = None   # dictionnary with format {'devicealias': SICK_SIG350_Sensor_Class}

    sensor_timeout = 5

    health_check_interval = 5
    health_check_retries = 10
    health_check_timeout = 10

    def __init__(self):
        # Configuration validations
        if self.ip_address is None:
            raise ImproperlyConfigured("SIG350Adapter requires the attribute 'ip_address' to be defined")
        if self.sensors is None:
            raise ImproperlyConfigured("SIG350Adapter requires the attribute 'sensors' to be defined")

        self.session = requests.Session()
        print("============================================================")
        print("MTConnect Adapter for SICK SIG350 Sensor Integration Gateway")
        print("(c) Concordia University DemoFactory 2024")
        print("============================================================")
        print("SIG350 connection configuration:")
        print(f" - URL: {self.ip_address}")

        # connect sensors
        print("\nConnected sensor(s):")
        self._identification = {}
        self.devices = {}
        for device_alias in self.sensors:
            self.devices[device_alias] = self.sensors[device_alias](self.session, self.ip_address, device_alias)
            self._identification[device_alias] = self.devices[device_alias].identification
            print(f" - On {device_alias}:")
            for key in self._identification[device_alias]:
                print("   -", key, ":", self._identification[device_alias][key])
            print()
        self.__available__ = 1

    def manufacturer(self):
        """ SIG350 manufacturer """
        dev_identification = requests.get(f"http://{self.ip_address}/iolink/v1/masters/1/identification",
                                          timeout=self.health_check_timeout).json()
        return dev_identification['vendorName']

    def serialNumber(self):
        """ SIG350 serial number """
        dev_identification = requests.get(f"http://{self.ip_address}/iolink/v1/masters/1/identification",
                                          timeout=self.health_check_timeout).json()
        return dev_identification['serialNumber']

    def health_check(self):
        """
        Return health status of SIG350 connection
        """
        self.session.close()
        healthy = False
        retries = 0
        print(f"Checking sensor connection on {self.ip_address} ...")
        while not healthy:
            try:
                retries += 1
                requests.get(f"http://{self.ip_address}", timeout=self.health_check_timeout)
                healthy = True
            except requests.exceptions.ConnectionError:
                if retries == self.health_check_retries:
                    return False
                print(f'Failed to connect to SIG350 (attempt #{retries})')
                healthy = False
                time.sleep(self.health_check_interval)
        self.session = requests.Session()
        print("Connection established")
        return True

    def read_data(self):
        """
        Read and return data from all connected sensors
        """
        ret = {}
        for device in self.devices:
            r = self.devices[device].read_data()
            if r:
                ret = ret | r
        return ret
