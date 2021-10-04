# Farm Device 1Wire Container

This container runs on the device that has the 1Wire i2c devices connected to it, and provides
an interface to the connected devices via the owfs package.

## Building and testing the container

```bash
cd farm_device/
docker build -t nstoik/farm_device_1wire:latest 1wire/
docker run --name 1_wire_test -d --publish 2121:2121 --device /dev/i2c-1:/dev/i2c-1 nstoik/farm_device_1wire:latest
```

after testing or whatever you needed it for, clean up with:
```bash
docker container stop 1_wire_test
docker container rm 1_wire_test
```

## Testing i2c
To test for valid i2c devices run the following command from the docker host:

```bash
docker exec fd_1wire i2cdetect -y 1
```

Sample output:
```
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:                         -- -- -- -- -- -- -- --
10: -- -- -- -- -- -- -- -- 18 19 -- -- -- -- -- --
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
70: -- -- -- -- -- -- -- --
```

## Accessing the web interface.
Access the webpage from the default port of 2121, or whatever override made with docker-compose.