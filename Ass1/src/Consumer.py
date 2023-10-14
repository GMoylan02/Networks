import socket
import threading
import time
import netifaces as ni
bufferSize = 1024


class Consumer:
    def __init__(self, consumer_id):
        self.consumer_id = consumer_id
        self.name = f'Consumer{consumer_id}'
        self.UDPsocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        ip = ni.ifaddresses('eth1')[ni.AF_INET][0]['addr']  # Getting eth1 ip as opposed to eth0
        self.UDPsocket.bind((ip, 50000))
        self.ping_received = False

    def consume(self):
        t1 = threading.Thread(target=self.__listen)
        t2 = threading.Thread(target=self.__ping, args=(2,))

        t1.start()
        t2.start()

        t1.join()
        t2.join()

    def __subscribe(self, stream_no, address):
        print(f'Consumer {self.consumer_id} subscribed to stream no '
              f'{int.from_bytes(stream_no, signed=False, byteorder="little")}!')
        # sender_id:3 - stream no:1 - frame_no:2 - is_announce:1 - ping_recd:1 - is_ping:1 - is_subscription:1 - audio_no:2
        header = self.consumer_id + stream_no + b'\x00\x00\x00\x00\x00\x01\x00\x00'
        self.UDPsocket.sendto(header, address)

    # Periodically pings the broker
    def __ping(self, interval):
        while not self.ping_received:
            # sender_id:3 - stream no:1 - frame_no:2 - is_announce:1 - ping_recd:1 - is_ping:1 - is_subscription:1 -audio_no:2
            header = self.consumer_id + b'\x00\x00\x00\x00\x00\x01\x00\x00\x00'
            print("Pinged Broker!")
            self.UDPsocket.sendto(header, ("Broker", 50000))
            time.sleep(interval)

    def __listen(self):
        print(f'Consumer {self.consumer_id} started listening!')
        while True:
            pair = self.UDPsocket.recvfrom(bufferSize)
            incoming_msg = pair[0]
            address = pair[1]

            # sender_id:3 - stream no:1 - frame_no:2 - is_announce:1 - ping_recd:1 - is_ping:1 - is_subscription:1 -audio_no:2
            sender_id = incoming_msg[0:3]
            stream_no = incoming_msg[3:4]
            frame_no = incoming_msg[4:6]
            is_announcement = incoming_msg[6:7] == b'\x01'
            ping_recd = incoming_msg[7:8] == b'\x01'
            is_ping = incoming_msg[8:9] == b'\x01'
            is_subscription = incoming_msg[9:10]
            audio_no = incoming_msg[10:12]

            audio_no_int = int.from_bytes(audio_no, signed=False, byteorder='little')
            stream_no_int = int.from_bytes(stream_no, signed=False, byteorder='little')
            frame_no_int = int.from_bytes(frame_no, signed=False, byteorder='little')

            if is_announcement and input(f"Do you want to subscribe to stream "
                                         f"{stream_no_int}?(Yes/No)").lower() == 'yes':
                self.__subscribe(stream_no, address)
                is_announcement = False
            elif sender_id == self.consumer_id and ping_recd:
                print("Received signal to stop pinging!")
                self.ping_received = True
            elif frame_no != b'\x00\x00' or audio_no != b'\x00\x00':
                if frame_no == b'\x00\x00':
                    print(f'Consumer {self.consumer_id} received frame no {frame_no_int} from producer {sender_id}!')
                else:
                    print(f'Consumer {self.consumer_id} received audio segment no {audio_no_int} from producer {sender_id}!')
