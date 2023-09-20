import socket
import os
localIP = "Producer"

localPort = 50000
bufferSize = 1024
video_path = '\..\First20Frames'

# TODO allow for 1 producer to have multiple streams
class Producer:
    def __init__(self, id: bytes, stream_no: bytes, number):
        self.id = id
        self.stream_no = stream_no
        self.header = id + stream_no
        self.number = number
        self.UDPsocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.UDPsocket.bind((localIP, localPort))

    # TODO Include functionality for the producer to wait for subscriptions before continuing
    def notify_broker(self):
        msg = str.encode(f"Announcing the topic contained in this header!")
        self.UDPsocket.sendto(self.header + 0x0000 + msg, ("Broker", 50000))

    # Publishes the videos as packets to the broker
    # Assumes the frames follow the file naming convention of "frame001.png" and so on
    # TODO implement functionality to send audio as well
    def publish(self):
        bytesToSend = None
        for i in range(1, 21):
            bytesToSend.extend(png_to_bytearray(f"{video_path}\frame{i:03d}.png"))
            self.UDPsocket.sendto(self.header + i.to_bytes(1, 'big') + 0x01 + bytesToSend[i-1], ("Broker", 50000))

# Given the filepath, converts a png file to a bytearray
def png_to_bytearray(filepath: str):
    with open(filepath, "rb") as img:
        return bytearray(img.read())
