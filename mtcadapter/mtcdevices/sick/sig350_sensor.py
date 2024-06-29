import requests


"""
Parent class for a sensor connected to a SIG350 Sensor Integration Gateway

Uses the SIG350 REST API to read sensor data
"""


class SICK_SIG350_Sensor():

    def __init__(self, session, ip_address, device_alias):
        self.session = session
        self.ip_address = ip_address
        self.device_alias = device_alias

    @property
    def status(self):
        """ Status of sensor """
        ret = self.session.get(f"http://{self.ip_address}/iolink/v1/devices/{self.device_alias}/parameters/36/value").json()
        return ret['value'][0]

    @property
    def identification(self):
        """ Identifcation data of sensor """
        return requests.get(f"http://{self.ip_address}/iolink/v1/devices/{self.device_alias}/identification").json()
