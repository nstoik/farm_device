FROM ubuntu:21.04

RUN sudo apt install i2c-tools owfs -y

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install i2c-tools owserver ow-shell owhttpd owfs-fuse -y && \
    apt-get autoremove -y && \
    apt-get autoclean && \
    rm -rf /var/lib/apt/lists/*

RUN sudo mkdir /mnt/1wire

COPY owf.confs /etc/owfs.conf

CMD ["/bin/bash"]