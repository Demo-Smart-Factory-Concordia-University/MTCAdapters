import requests
import os
import time
from mtcadapter.mtcdevices import MTCDevice
from mtcadapter.exceptions import ImproperlyConfigured


"""
SICK AG Proximity sensor connected to a SIG350 Sensor Integration Gateway

Uses the SIG350 REST API to read sensor data
"""


class SICKProximitySensor(MTCDevice):

    ip_address = os.getenv('SIG350_IP') or None
    device_alias = os.getenv('DEVICE_ALIAS') or None

    sensor_timeout = 5

    health_check_interval = 5
    health_check_retries = 10
    health_check_timeout = 10

    __available__ = 0

    def __init__(self):
        # Configuration validations
        if self.ip_address is None:
            raise ImproperlyConfigured("SICKProximitySensor requires the attribute 'ip_address' to be defined")
        if self.device_alias is None:
            raise ImproperlyConfigured("SICKProximitySensor requires the attribute 'device_alias' to be defined")
        self.session = requests.Session()

    def manufacturer(self):
        dev_identification = requests.get(f"http://{self.ip_address}/iolink/v1/masters/1/identification",
                                          timeout=self.health_check_timeout).json()
        return dev_identification['vendorName']

    def serialNumber(self):
        dev_identification = requests.get(f"http://{self.ip_address}/iolink/v1/masters/1/identification",
                                          timeout=self.health_check_timeout).json()
        return dev_identification['serialNumber']

    def health_check(self):
        """
        Return health status of device connection
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
                print(f'Failed to connect to sensor (attempt #{retries})')
                healthy = False
                time.sleep(self.health_check_interval)
        self.session = requests.Session()
        print("Connection established")
        return True

    def read_data(self):
        """
        Read and return device data
        """
        try:
            resp = self.session.get(f"http://{self.ip_address}/iolink/v1/devices/{self.device_alias}/processdata/value",
                                    timeout=self.sensor_timeout).json()
        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
            self.__available__ = 0
            return {'avail': 'UNAVAILABLE'}
        if self.__available__ == 0:
            self.__available__ = 1
            return {'avail': 'AVAILABLE'}
        if resp['getData']['cqValue']:
            return {'trigger': '1'}
        else:
            return {'trigger': '0'}
