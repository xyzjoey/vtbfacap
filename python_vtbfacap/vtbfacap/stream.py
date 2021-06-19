import socket

from .settings import settings

class OutputStream:
    def __init__(self, host=settings.host, port=settings.port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP

    def __del__(self):
        self.socket.close()

    def send(self, data):
        print(f"send({self.host}, {self.port}): {data}")
        self.socket.sendto(data, (self.host, self.port))
