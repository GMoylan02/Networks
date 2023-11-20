FROM ubuntu:latest
RUN apt-get update && \
    apt-get install -y tcpdump && \
    rm -f /pcap/capture.pcap
CMD ["tcpdump", "-i", "any", "-nn", "-vvv", "-w", "/pcap/capture.pcap"]