"""
MTConnect Adapter for the WTVB01-485 vibration sensor from WitMotion

Uses RS485 Modbus RTU for communication
"""

import minimalmodbus
import termios
import os
import time
from mtcadapter.mtcdevices import MTCDevice
from mtcadapter.exceptions import ImproperlyConfigured


class WTVB01(MTCDevice):

    # default factory configuration
    baud_rate = 9600
    sensor_address = 80

    # MTConnect IDs
    # If set to None, will not return the value to the Agent
    temperature_id = 'temp'
    dx_id = 'dx'
    dy_id = 'dy'
    dz_id = 'dz'
    hx_id = 'hx'
    hy_id = 'hy'
    hz_id = 'hz'

    DEBUG = False

    # sensor registers
    TEMP_REGISTER = 64
    DX_REGISTER = 65
    HZX_REGSTER = 68

    __available__ = 1

    def __init__(self):
        # Configuration validations
        if self.port is None:
            raise ImproperlyConfigured("WTVB01 requires the attribute 'port' to be defined")

        # Checks if a device is connected to the serial port
        if not self._check_port():
            print(f'No device connected to {self.port}')
            print('Will attempt continously every 10 seconds')
            while not self._check_port():
                time.sleep(10)

        self.sensor = minimalmodbus.Instrument(self.port,
                                               self.sensor_address,
                                               mode=minimalmodbus.MODE_RTU,
                                               debug=self.DEBUG)
        self.sensor.serial.baudrate = self.baud_rate
        self.sensor.close_port_after_each_call = False
        self.sensor.clear_buffers_before_each_transaction = True

        print("============================================================")
        print("MTConnect Adapter for WTVB01-485 vibration sensor")
        print("(c) Concordia University DemoFactory 2024")
        print("============================================================")

    def _check_port(self):
        """
        Attempts to open the serial port
        """
        try:
            f_id = os.open(self.port, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
            os.close(f_id)
            return True
        except FileNotFoundError:
            return False

    def health_check(self):
        """
        Return health status of device connection
        """
        try:
            self.temperature()
            self.__available__ = 1
            return True
        except IOError:
            self.__available__ = 0
            return False

    def manufacturer(self):
        """ WTVB01-485 manufacturer """
        return 'WitMotion'

    def temperature(self):
        """
        Read temperature in degree Celcius
        """
        return round(self.sensor.read_register(self.TEMP_REGISTER) / 100, 1)

    def displacements(self):
        """
        Read displacements in microns
        """
        return self.sensor.read_registers(self.DX_REGISTER, 3)

    def vibration_frequencies(self):
        """
        Read vibration frequencies in Hz
        """
        return self.sensor.read_registers(self.HZX_REGSTER, 3)

    def read_data(self):
        """
        Read and return device data
        """
        try:
            temp = self.temperature()
            disp = self.displacements()
            freq = self.vibration_frequencies()
        except (IOError, termios.error):
            self.__available__ = 0
            self.sensor.serial.close()
            return {'avail': 'UNAVAILABLE'}

        if self.__available__ == 0:
            if self.health_check():
                return {'avail': 'AVAILABLE'}

        return {
            key: value
            for key, value in {
                self.temperature_id: temp,
                self.dx_id: disp[0],
                self.dy_id: disp[1],
                self.dz_id: disp[2],
                self.hx_id: freq[0],
                self.hy_id: freq[1],
                self.hz_id: freq[2],
            }.items()
            if key is not None
        }
