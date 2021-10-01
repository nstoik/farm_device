#!/bin/bash

echo "Starting all services"

/usr/bin/owserver --foreground --debug -c /etc/owfs.conf

# Spin until we receive a SIGTERM (e.g. from `docker stop`)
echo "all work done, go sleeping..."
trap 'exit 143' SIGTERM # exit = 128 + 15 (SIGTERM)
tail -f /dev/null & wait ${!}