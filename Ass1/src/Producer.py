import socket
import os
localIP = "Producer"

localPort = 50000
bufferSize = 1024
video_path = '\..\First20Frames'

class Producer:
    def __init__(self, id: bytes, stream_no: bytes):
        self.id = id
        self.stream_no = stream_no
        self.header = id + stream_no
        self.UDPsocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    # TODO notifies a broker that a new stream is about to begin
    def notify_broker(self):
        pass

    # Publishes the videos as packets to the broker
    # Assumes the frames follow the file naming convention of "frame001.png" and so on
    def publish(self):
        bytesToSend = None
        for i in range(1, 21):
            bytesToSend.extend(png_to_bytearray(f"{video_path}\frame{i:03d}.png"))
        for byte in bytesToSend:
            self.UDPsocket.sendto(self.header + byte, ("Broker", 50000))


# Given the filepath, converts a png file to a bytearray which can then
# Be used as the payload for a packet and sent to the broker
def png_to_bytearray(filepath: str):
    with open(filepath, "rb") as img:
        return bytearray(img.read())
