import sys
import socketserver
from mtcadapter.exceptions import ImproperlyConfigured


class MTCAdapter(socketserver.TCPServer):
    """
    Implements a MTConnect Adapter as a TCP server
    Handles requests from the Agent with agentRequestHandler_class
    """

    adapter_port = 7878
    agentRequestHandler_class = None

    def __init__(self):
        """
        Constructor
        """
        # Configuration validations
        if self.agentRequestHandler_class is None:
            raise ImproperlyConfigured("MTCAdapterRelay requires the attribute 'deviceHandler_class' to be defined")

        print(f"Starting Adapter on port {self.adapter_port}")
        socketserver.TCPServer.__init__(self, ('', self.adapter_port), self.agentRequestHandler_class)

    def run(self):
        """
        Run the adapter
        """
        try:
            self.serve_forever()
        except KeyboardInterrupt:
            sys.exit(0)
