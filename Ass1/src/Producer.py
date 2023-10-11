import socket
import time
import threading

localIP = "Producer"

localPort = 50000
bufferSize = 1024
video_path = '/First20Frames'


class Producer:
    def __init__(self, producer_id: bytes):
        self.producer_id = producer_id
        self.name = 'Producer'
        self.UDPsocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.UDPsocket.bind(("Producer", localPort))
        self.ping_received = False
        self.stream_ids = []

    def produce(self):
        t1 = threading.Thread(target=self.__new_stream(), args=())
        t2 = threading.Thread(target=self.__ping(), args=(0.5,))
        t3 = threading.Thread(target=self.__listen_for_updates(), args=())

        t1.start()
        t2.start()
        t3.start()

        t1.join()
        t2.join()
        t3.join()

    def __new_stream(self):
        while True:
            print(f"Producer id {self.producer_id} started a new stream!")
            stream_no = self.__find_unused_stream_id()

            choice = input('Type "notify" to notify possible consumers of your stream!!')
            while choice.lower() != 'notify':
                choice = input('Type "notify" to notify possible consumers of your stream!!')
            self.__notify_broker(stream_no)

            choice = input('Type "publish" to publish the stream!')
            while choice.lower() != 'publish':
                choice = input('Type "publish" to publish the stream!')
            self.__publish(stream_no)

            choice = input('Type "restart" to start a new stream!')
            while choice.lower() != 'restart':
                input('Type "restart" to start a new stream!')

    def __ping(self, interval):
        while not self.ping_received:
            time.sleep(interval)
            # sender_id:3 - stream no:1 - frame_no:1 - is_announce:1 - ping_recd:1 - is_ping:1 - is_subscription:1
            header = self.producer_id + b'\x00\x00\x00\x00\x01\x00'
            print("Pinged Broker!")
            self.UDPsocket.sendto(header, ("Broker", 50000))

    def __listen_for_updates(self):
        while True:
            pair = self.UDPsocket.recvfrom(bufferSize)
            incoming_msg = pair[0]
            stream_no = incoming_msg[3:4]
            ping_recd = incoming_msg[6:7] == b'\x01'

            if stream_no != b'\x00':
                # Must be stream id update
                self.stream_ids.append(int.from_bytes(stream_no, signed=False, byteorder='little'))
            elif ping_recd:
                # Must be a ping received
                self.ping_received = True

    def __notify_broker(self, stream_no):
        print(f'Producer {self.producer_id} is announcing stream no {stream_no}!')
        msg = str.encode(f"Announcing the topic contained in this header!")
        # sender_id:3 - stream no:1 - frame_no:1 - is_announce:1 - ping_recd:1 - is_ping:1 - is_subscription:1
        header = self.producer_id + stream_no.to_bytes(1, 'big') + b'\x00\x01\x00\x00\x00'
        self.UDPsocket.sendto(header + msg, ("Broker", 50000))

    # Publishes the videos as packets to the broker
    # Assumes the frames follow the file naming convention of "frame001.png" and so on
    # TODO implement functionality to send audio as well
    # TODO functionality to start a new stream
    def __publish(self, stream_no):
        print(f'Producer {self.producer_id} started publishing stream no {stream_no}!')
        for i in range(1, 21):
            # sender_id:3 - stream no:1 - frame_no:1 - is_announce:1 - ping_recd:1 - is_ping:1 - is_subscription:1
            header = self.producer_id + stream_no.to_bytes(1, 'big') + i.to_bytes(1, 'big') + b'\x00\x00\x00\x00'
            self.UDPsocket.sendto(header + bytes(png_to_bytearray(f"{video_path}/frame{i:03d}.png")), ("Broker", 50000))

    def __find_unused_stream_id(self):
        if len(self.stream_ids) == 0:
            return 1
        else:
            return self.stream_ids[-1]+1


# Given the filepath, converts a png file to a bytearray
def png_to_bytearray(filepath: str):
    with open(filepath, "rb") as img:
        t = bytearray(img.read())
        return t
