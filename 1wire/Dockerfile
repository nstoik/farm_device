FROM ubuntu:21.04

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install i2c-tools owserver ow-shell owhttpd owfs-fuse -y && \
    apt-get autoremove -y && \
    apt-get autoclean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir /mnt/1wire

COPY owfs.conf /etc/owfs.conf

CMD ["/bin/bash"]