FROM ubuntu
WORKDIR /compnets
RUN apt-get update -y 
RUN apt-get install -y net-tools netcat tcpdump inetutils-ping
RUN apt-get install -y python3-pip
RUN pip install -i https://test.pypi.org/simple/ Ass1-gmoylan
CMD ["/bin/bash"]
CMD ["pip install --upgrade -i https://test.pypi.org/simple/ Ass1-gmoylan"]
