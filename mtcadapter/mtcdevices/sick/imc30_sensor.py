import requests
from .sig30_sensor import SICK_SIG350_Sensor


"""
SICK AG IMC30 inductive proximity sensor connected to a SIG350 Sensor Integration Gateway
Uses the SIG350 REST API to read sensor data
"""


class SICK_IMC30_Sensor(SICK_SIG350_Sensor):

    sensor_timeout = 5

    health_check_interval = 5
    health_check_retries = 10
    health_check_timeout = 10

    # MTConnect DataItem ID
    trigger_id = 'trigger'

    # Trigger threshold
    threshold = 15

    __available__ = 1

    def read_data(self):
        """
        Read and return device data
        """
        try:
            resp = self.session.get(f"http://{self.ip_address}/iolink/v1/devices/{self.device_alias}/processdata/getdata/value",
                                    timeout=self.sensor_timeout).json()
        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
            self.__available__ = 0
            return {'avail': 'UNAVAILABLE'}

        if 'iolink' not in resp:
            return None

        if self.__available__ == 0:
            self.__available__ = 1
            return {'avail': 'AVAILABLE'}

        if resp['iolink']['value'][0] > self.threshold:
            return {self.trigger_id: '0'}
        else:
            return {self.trigger_id: '1'}
