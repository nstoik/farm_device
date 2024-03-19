FROM ubuntu:24.04

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install curl i2c-tools owserver ow-shell owhttpd -y && \
    apt-get autoremove -y && \
    apt-get autoclean && \
    rm -rf /var/lib/apt/lists/*

COPY 1wire/start.sh /start.sh

RUN ["chmod", "+x", "/start.sh"]

COPY 1wire/owfs.conf /etc/owfs.conf

EXPOSE 2121

ENTRYPOINT ["/start.sh"]

HEALTHCHECK --interval=60s --timeout=3s \
  CMD curl -f http://localhost:2121/ || exit 1