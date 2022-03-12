# Farm Device
Main documentation for the Farm Device project.

# Production
To run farm_device in production, execute the following docker-compose command from the root of the project:
``` bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml -p fd_prod up -d --no-build
```

To bring down the stack, run:
``` bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml -p fd_prod down
```

# Development

# VS Code Development
VS Code automatically builds the required containers when you launch into a remote container. This uses the `docker-compose.devcontainer.yml` overrides.

To bring the farm device stack down and remove the containers, run:
``` bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml -f docker-compose.devcontainer.yml -p fd_dev down
```
# Raspberry Pi Ubuntu 21.04 host setup

Add the required packages by running the following commands.

TODO: Add docker setup steps

```bash
sudo apt install i2c-tools
```

Add the following line to ```/boot/firmware/config.txt```

```dtoverlay=w1-gpio```
