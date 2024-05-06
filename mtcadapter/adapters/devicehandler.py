import socket
import socketserver
import getpass
import mtcadapter
from mtcadapter.exceptions import ImproperlyConfigured
from mtcadapter.mtcdevices import MTCDevice


class DeviceHandler(socketserver.BaseRequestHandler):
    """
    Reads SHDR data from a MTCDevice
    Defintion of the Adapter Agent protocol : https://www.mtcup.org/Protocol
    """

    device_class = None
    HEARTBEAT_TIMEOUT = 10000

    __data_old__ = {}

    def __init__(self, request, client_address, server):
        """
        Constructor
        """
        # Configuration validations
        if self.device_class is None:
            raise ImproperlyConfigured("DeviceHandler requires the attribute 'device_class' to be defined")
        if not issubclass(self.device_class, MTCDevice):
            raise ImproperlyConfigured("DeviceHandler attribute 'device_class' has to be a subclass of MTCDevice")

        self.device = self.device_class()
        socketserver.BaseRequestHandler.__init__(self, request, client_address, server)

    def send_shdr(self, data):
        """
        Send SHDR data to agent
        """
        for id in data:
            self.request.sendall((f"|{id}|{data[id]}\n").encode())

    def handle(self):
        """
        Handle connection from MTConnect Agent
        """
        print("Connection from {}".format(self.client_address[0]))
        if self.device.health_check():
            self.request.sendall(("|avail|AVAILABLE\n").encode())
        else:
            self.request.sendall(("|avail|UNAVAILABLE\n").encode())
            return
        self.request.settimeout(0.01)

        # send initial SHDR data
        self.request.sendall(("|operator|" + getpass.getuser() + "\n").encode())
        self.request.sendall(("* shdrVersion: 2.0\n").encode())
        self.request.sendall((f"* adapterVersion: {mtcadapter.__version__}\n").encode())
        manufacturer = self.device.manufacturer()
        serialNumber = self.device.serialNumber()
        if manufacturer:
            self.request.sendall((f"* manufacturer: {manufacturer}\n").encode())
        if serialNumber:
            self.request.sendall((f"* serialNumber: {serialNumber}\n").encode())
        self.send_shdr(self.device.read_data())
        self.send_shdr(self.device.on_connect())

        while 1:
            try:
                data = self.request.recv(1024)
            except socket.timeout:
                device_data = self.device.read_data()
                for id in device_data:
                    if id not in self.__data_old__:
                        self.__data_old__[id] = ''
                    if device_data[id] != self.__data_old__[id]:
                        self.request.sendall((f"|{id}|{device_data[id]}\n").encode())
                        if id != 'avail':
                            self.__data_old__[id] = device_data[id]
                continue

            if not data:
                print("Connection from Agent closed")
                break

            if data == "* PING\r\n".encode():
                self.request.sendall(f"* PONG {str(self.HEARTBEAT_TIMEOUT)}\n".encode())
