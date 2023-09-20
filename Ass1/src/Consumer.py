import socket
bufferSize = 1024
class Consumer:
    def __init__(self, number):
        self.name = f'Consumer{number}'
        self.header = number.toBytes(1, 'big')
        self.UDPsocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.UDPsocket.bind((self.name, 50000))

    # Where stream_id is the producer id + stream_no
    def subscribe(self, stream_id):
        self.header = self.header + stream_id

