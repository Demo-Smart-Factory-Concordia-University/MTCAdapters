class MTCDevice():
    """
    Base class for MTCDevices
    """

    def manufacturer(self):
        """
        Return device manufacturer
        """
        return None

    def serialNumber(self):
        """
        Return device serial number
        """
        return None

    def on_connect(self):
        """
        Send initial data when MTConnect Agent connects
        """
        return {}

    def health_check(self):
        """
        Return health status of device connection
        """
        return True

    def read_data(self):
        """
        Read and return device data
        """
        return {}
