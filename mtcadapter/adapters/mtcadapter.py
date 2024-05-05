import sys
import socketserver
from mtcadapter.exceptions import ImproperlyConfigured


class MTCAdapter(socketserver.TCPServer):
    """
    Implements a MTConnect Adapter server
    Reads SHDR data from deviceHandler_class
    """

    adapter_port = 7878
    deviceHandler_class = None

    def __init__(self):
        """
        Constructor
        """
        # Configuration validations
        if self.deviceHandler_class is None:
            raise ImproperlyConfigured("MTCAdapterRelay requires the attribute 'deviceHandler_class' to be defined")

        print(f"Starting Adapter on port {self.adapter_port}")
        socketserver.TCPServer.__init__(self, ('', self.adapter_port), self.deviceHandler_class)

    def run(self):
        """
        Run the adapter
        """
        try:
            self.serve_forever()
        except KeyboardInterrupt:
            sys.exit(0)
