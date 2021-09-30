FROM ubuntu:21.04

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install i2c-tools owserver ow-shell owhttpd owfs-fuse -y && \
    apt-get autoremove -y && \
    apt-get autoclean && \
    rm -rf /var/lib/apt/lists/*

COPY start.sh /start.sh

RUN ["chmod", "+x", "/start.sh"]

COPY owfs.conf /etc/owfs.conf

# Run forever
# CMD exec /bin/bash -c "trap : TERM INT; sleep infinity & wait"

ENTRYPOINT ["/start.sh"]