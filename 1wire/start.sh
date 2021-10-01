#!/bin/bash

echo "Starting owserver"
/usr/bin/owserver -c /etc/owfs.conf
echo "Starting owhttpd"
/usr/bin/owhttpd -c /etc/owfs.conf

# Spin until we receive a SIGTERM (e.g. from `docker stop`)
echo "all services started, sleeping forever..."
trap 'exit 143' SIGTERM # exit = 128 + 15 (SIGTERM)
tail -f /dev/null & wait ${!}