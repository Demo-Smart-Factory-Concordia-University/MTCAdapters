import requests
from .sig30_sensor import SICK_SIG350_Sensor


"""
SICK AG AHS/AHM36 absolute encoder connected to a SIG350 Sensor Integration Gateway
Uses the SIG350 REST API to read sensor data
"""


class SICK_AHS_AHM36_Sensor(SICK_SIG350_Sensor):

    sensor_timeout = 5

    health_check_interval = 5
    health_check_retries = 10
    health_check_timeout = 10

    # MTConnect DataItem IDs
    rotary_velocity_id = 'rotary_velocity'
    velocity_id = 'velocity'

    __available__ = 1

    def __init__(self, session, ip_address, device_alias, velocity_format=3, radius=None):
        super().__init__(session, ip_address, device_alias)
        self.velocity_format = velocity_format
        self.radius = radius

    @property
    def velocity_format(self):
        ret = self.session.get(f"http://{self.ip_address}/iolink/v1/devices/{self.device_alias}/parameters/66/value").json()
        self._velocity_format = ret['value'][0]
        return ret['value'][0]

    @velocity_format.setter
    def velocity_format(self, velocity_format):
        self._velocity_format = velocity_format
        self.session.post(f"http://{self.ip_address}/iolink/v1/devices/{self.device_alias}/parameters/66/value",
                          json={'value': [velocity_format]})

    def read_data(self):
        """
        Read and return device data
        """
        try:
            resp = self.session.get(f"http://{self.ip_address}/iolink/v1/devices/{self.device_alias}/parameters/65/value",
                                    timeout=self.sensor_timeout).json()
        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
            self.__available__ = 0
            return {'avail': 'UNAVAILABLE'}
        if self.__available__ == 0:
            self.__available__ = 1
            return {'avail': 'AVAILABLE'}
        raw_value = int.from_bytes(bytes(resp['value']), "big", signed=True)
        if self._velocity_format == 3:
            value = raw_value
        if self._velocity_format == 4:
            value = raw_value*60.0
        if self.radius:
            return {self.rotary_velocity_id: value, self.velocity_id: value*self.radius/60.0}
        return {self.rotary_velocity_id: value}
