import socket
import threading
import time

bufferSize = 1024


class Consumer:
    def __init__(self, consumer_id):
        self.consumer_id = consumer_id
        self.name = f'Consumer{consumer_id}'
        self.UDPsocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.UDPsocket.bind(('Consumer', 50000))

    def consume(self):
        t1 = threading.Thread(target=self.__listen, args=())
        t2 = threading.Thread(target=self.__ping, args=(0.5,))

        t1.start()
        t2.start()

        t1.join()
        t2.join()

    def __subscribe(self, stream_no, producer_id, address):
        print(f'Consumer {self.consumer_id} subscribed to stream no {stream_no}!')
        header = self.consumer_id + stream_no + b'\x00' + producer_id
        self.UDPsocket.sendto(header, address)

    # Periodically pings the broker
    def __ping(self, interval):
        while True:
            time.sleep(interval)
            header = self.consumer_id + b'\x00\x01' + b'\x00\x00\x00'
            print("Pinged Broker!")
            self.UDPsocket.sendto(header, ("Broker", 50000))

    def __listen(self):
        print(f'Consumer {self.consumer_id} started listening!')
        while True:
            pair = self.UDPsocket.recvfrom(bufferSize)
            incoming_msg = pair[0]
            address = pair[1]
            producer_id = incoming_msg[0:3]
            stream_no = incoming_msg[3:4]
            frame_no = incoming_msg[4:5]
            is_announcement = incoming_msg[5:6] == 0x00

            if (is_announcement and input(f"Do you want to subscribe to stream {stream_no}?(Yes/No)").lower() == 'yes'
                    or 'y'):
                self.__subscribe(stream_no, producer_id, address)
            else:
                print(f'Consumer {self.consumer_id} received frame no {frame_no} from producer {producer_id}!')




