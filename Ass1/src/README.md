Gerard Moylan 21364007

To run this:
1. Create docker containers on the same network for any number of Producers, and number of Consumers, and 1 Broker.

2. Run docker compose to install the pip packages on the Producer and Consumer containers.
2.5 (If this doesn't work, manually install pip on all the containers and then run "pip install -i https://test.pypi.org/simple/ Ass1-gmoylan")

3. Create a python script in each container which imports Producer or Consumer, then does
consumer1 = Consumer(ANY 3 BYTE ID)<br />
consumer1.consume()<br />
OR<br />
producer1 = Producer(ANY 3 BYTE ID)<br />
producer1.produce()

4. Copy the frames and audio into the base directory of every Producer container.

5. Run Broker.py in the Broker container and all the producer and consumers scripts you have made in the Producer 
and Consumer containers
