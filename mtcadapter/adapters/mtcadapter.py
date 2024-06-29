import sys
import socket
import socketserver
import getpass
import mtcadapter
from mtcadapter.exceptions import ImproperlyConfigured


class AgentRequestHandler(socketserver.BaseRequestHandler):
    """
    Handles requests from the MTConnect Agent
    Reads data from a MTCDevice and sends them in SHDR format to the connected agent
    Defintion of the Adapter Agent protocol : https://www.mtcup.org/Protocol
    """

    HEARTBEAT_TIMEOUT = 10000
    DEBUG = False

    __data_old__ = {}

    def __init__(self, request, client_address, server):
        """
        Constructor
        """
        self.device = server.device
        socketserver.BaseRequestHandler.__init__(self, request, client_address, server)

    def send_shdr(self, data):
        """
        Send SHDR data to agent
        """
        for id in data:
            if id not in self.__data_old__:
                self.__data_old__[id] = ''
            if data[id] != self.__data_old__[id]:
                self.request.sendall((f"|{id}|{data[id]}\n").encode())
                if self.DEBUG:
                    print(f"|{id}|{data[id]}")
                if id != 'avail':
                    self.__data_old__[id] = data[id]

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
                self.send_shdr(device_data)
                continue

            if not data:
                print("Connection from Agent closed")
                break

            if self.DEBUG:
                print("Agent sent:", data.decode())

            if "* PING" in data.decode():
                self.request.sendall(f"* PONG {str(self.HEARTBEAT_TIMEOUT)}\n".encode())
                if self.DEBUG:
                    print(f"* PONG {str(self.HEARTBEAT_TIMEOUT)}")


class MTCAdapter(socketserver.TCPServer):
    """
    Implements a MTConnect Adapter as a TCP server
    Handles requests from the Agent with agentRequestHandler_class
    """

    adapter_port = 7878
    device_class = None
    agentRequestHandler_class = AgentRequestHandler

    def __init__(self):
        """
        Constructor
        """
        # Configuration validations
        if self.device_class is None:
            raise ImproperlyConfigured("MTCAdapter requires the attribute 'device_class' to be defined")

        print("Setting up connection to device")
        self.device = self.device_class()

        print("Creating Adapter")
        socketserver.TCPServer.__init__(self, ('', self.adapter_port), self.agentRequestHandler_class)

    def run(self):
        """
        Run the adapter
        """
        print(f"Starting Adapter on port {self.adapter_port}")
        try:
            self.serve_forever()
        except KeyboardInterrupt:
            sys.exit(0)
