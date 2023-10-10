FROM ubuntu
WORKDIR /compnets
RUN apt-get update -y 
RUN apt-get install -y net-tools netcat tcpdump inetutils-ping
RUN apt-get install -y python3-pip
CMD ["/bin/bash"]
CMD ["pip install -i https://test.pypi.org/simple/ Ass1-gmoylan==0.0.1"]
