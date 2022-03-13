# Farm Device
Main documentation for the Farm Device project.

# Environment Variables
There is a set of environment variables that can be used to configure the application. In the GitHub repository, an example configuration file is available in the root directory as `.env.example`.

There are SECRET variables and there are CONFIGURATION variables.

This file has a `FD_GENERAL_CONFIG` variable at the top that controls the general configuration of the different mono repos. Hint: change this variable between 'dev', 'prod', or 'test'.

The majority of the docker commands use the `.env` file by default to configure the containers. Edit the `.env` file as needed for the specific environment (including setting SECRET and TOKEN variables).

The `docker buildx bake` commands use configuration variables in the `docker-bake.hcl` file. These can be overridden as shown below when building images using `docker buildx bake`.

The containers use environment variables when the stack is brought up (environment variables). Some containers require build-args to be applied at build time instead.

Each monorepo can have its own set of environment variables if applicable. This are used for local development and testing. An example configuration file is available in the monorepo directory as `.env.example`.

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
