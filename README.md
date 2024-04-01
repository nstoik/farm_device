# Farm Device
Main documentation for the Farm Device project.

# Table of Contents
1. [Raspberry Pi Ubuntu 21.04 host setup](#Raspberry-Pi-Ubuntu-21.04-host-setup)
    1. [Installing Docker and Docker Compose](#Installing-Docker-and-Docker-Compose)
    2. [Additional Host Setup](#Additional-Host-Setup)
2. [First Time Setup](#First-Time-Setup)
3. [Environment Variables](#Environment-Variables)
4. [Production](#Production)
5. [Development](#Development)
    1. [Remote vs Local Development](#Remote-vs-Local-Devlopment)
    2. [Docker Commands](#Docker-Commands)
6. [VS Code Development](#VS-Code-Development)
7. [Building Docker Containers](#Building-Docker-Containers)
    1. [Login to Docker Hub](#Login-to-Docker-Hub)
    2. [Build single platform container](#Build-single-platform-container)
    3. [Bulid multiple containers for a single platform](#Build-multiple-containers-for-a-single-platform)
    4. [Building multi platform containers and pushing to a registry](#Building-multi-platform-containers-and-pushing-to-a-registry)
8. [Publishing Versions](#Publishing-Versions)
    1. [Git Branches](#Git-Branches)
    2. [Publishing Changes](#Publishing-Changes)

# Raspberry Pi Ubuntu 21.04 host setup

## Installing Docker and Docker Compose

To install Docker and Docker Compose, follow the steps from the [Docker Webpage](https://docs.docker.com/engine/install/ubuntu/#install-docker-engine)

## Additional Host Setup
Add the required packages by running the following commands.

```bash
sudo apt install i2c-tools
```

Add the following line to ```/boot/firmware/config.txt```

```dtoverlay=w1-gpio```

# First Time Setup
1. Pull the latest code from the repository.
2. Copy the `.env.example` file to `.env` and edit the values to match your setup.
3. Pull the docker images down to the host machine (see [Production](#Production))
4. Start the docker containers (see [Production](#Production))
5. When starting, the `fd_device` container will check the database if the first time setup has been run.
    * If it has, the application will start normally.
    * If it has not, the application will notify the user to run the first time setup and then exit.
        * To go through the first time setup, run the following docker command (with the other docker containers still running):
            ```bash
            docker run --rm -it --network=farm_device -e "FD_DEVICE_CONFIG=dev" nstoik/fd_device:dev /bin/bash -c "pipenv run fd_device first-setup"
            ```
        * Set the `FD_DEVICE_CONFIG` environment variable to as needed
        * Set the image tag to match the container
        * IF a standalone device, add `--standalone` to the command
        * Go through the first time setup steps.
        * Restart the containers (see [Production](#Production))


# Environment Variables
There is a set of environment variables that can be used to configure the application. In the GitHub repository, an example configuration file is available in the root directory as `.env.example`.

There are SECRET variables and there are CONFIGURATION variables.

This file has a `FD_GENERAL_CONFIG` variable at the top that controls the general configuration of the different mono repos. Hint: change this variable between 'dev', 'prod', or 'test'.

The majority of the docker commands use the `.env` file by default to configure the containers. Edit the `.env` file as needed for the specific environment (including setting SECRET and TOKEN variables).

The `docker buildx bake` commands use configuration variables in the `docker-bake.hcl` file. These can be overridden as shown below when building images using `docker buildx bake`.

The containers use environment variables when the stack is brought up (environment variables). Some containers require build-args to be applied at build time instead.

Each monorepo can have its own set of environment variables if applicable. This are used for local development and testing. An example configuration file is available in the monorepo directory as `.env.example`.

# Production
**Make sure to set the appropriate environment variables**

To run farm_device in production, execute the following docker-compose command from the root of the project:
``` bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env -p fd_prod up -d --no-build
```

To bring down the stack, run:
``` bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env -p fd_prod down
```

# Development
**Make sure to set the appropriate environment variables**

## Remote vs Local Devlopment
Some of the file paths in the development files are configured differently depending on whether you are developing locally (on the same machine) or remotely (eg. a Raspberry Pi). These files include:
* `.vscode\settings.json`
* `..\.devcontainer\devcontainer.json`
    * one under the device subfolder
    * one under the 1wire subfolder
* `docker-compose.devcontainer.yml`
    * change the workspace mount
* `docker-compose.yml`
    * comment out the `1w_bus_master` mount on the fd_device container for local development
    * comment out the `i2c` device on the fd_1wire container for local development

## Docker Commands
To run the farm_device in development, execute the following docker-compose command from the root of the project:

Note the different second file paramater, `-f docker-compose.dev.yml` flag. This is for the development environment.

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env -p fd_dev up -d
```

To bring down the stack run:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env -p fd_dev down
```

# VS Code Development
VS Code automatically builds the required containers when you launch into a remote container. This uses the `docker-compose.devcontainer.yml` overrides.

To bring the farm device stack down and remove the containers, run:
``` bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml -f docker-compose.devcontainer.yml down
```

# Building Docker Containers
There are multiple options for building the docker containers

## Login to Docker Hub
To login to docker hub, execute the following command and enter your credentials:
```bash
docker login
```

This is required to push the containers to docker hub.

## Build single platform container
To build a single docker container for a single platform, execute the following command:
```bash
docker build {PATH} --file {PATH}/Dockerfile --no-cache --pull --build-arg {ENV NAME}={ENV VALUE} --tag nstoik/{module}:{tag}
```
An example command for building the fd_device container version 1.0.0-rc is:
```bash
docker build . --file device/Dockerfile --no-cache --pull --tag nstoik/fd_device:1.0.0-rc
```
- {PATH} is the context of the build
- --build-arg is optional and can pass in environment variables to docker build. It can be repeated for multiple variables.
    - {ENV NAME} is the name of the environment variable
    - {ENV VALUE} is the value of the environment variable
- {module} is the name of the module
- {tag} is the tag of the docker image

## Bulid multiple containers for a single platform
To build multiple docker containers for a single platform, execute the following command:
```bash
docker compose --file {docker-compose file} --env-file {env file} build --no-cache --pull
```
An example command for building all containers for prod is below. Upddate the `FD_TAG` variable in the environment file to the tag you want to build.
```bash
docker compose --file docker-compose.yml --file docker-compose.prod.yml --env-file .env build --no-cache --pull
```

To push the containers to the docker hub, execute the following command:
```bash
docker compose --file {docker-compose file} --env-file {env file} push
```
- {docker-compose file} is the docker-compose file
- {env file} is the .env file

## Building multi platform containers and pushing to a registry
First setup the prequisites. Configure buildx tools
```bash
docker buildx create --name fd_buildx
``` 
To list the available builders run:
```bash
docker buildx ls
```

Bake all the containers. In the example below, the TAGS variable is set to the tag (or comma seperated string of multiple tags) you want to build.
```bash
TAGS=0.1 docker buildx bake --builder fd_buildx --file docker-bake.hcl --push
```

To bake a single target or group specified in the `docker-bake.hcl` configuration file, run the following, replacing "TARGET_NAME" with the target or group name:
```bash
TAGS=0.1 docker buildx bake --builder fd_buildx --file docker-bake.hcl --push "TARGET_NAME"
```


**Note** Overwrite variables defined in the `docker-bake.hcl` file by specifying them as arguments to the command. Any required `ARG` in the docker files need to be specified in the `docker-bake.hcl` file.

The list of available variables are:
- TAGS: The tag of the docker image to build. Defaults to "dev". Can be a comma separated list of tags to apply multiple tags eg. "dev,latest".
- MULTI_STAGE_TARGET: The target to build. Defaults to "prod-stage"

A few additional comments on the `docker-bake.hcl` file:
- print is optional and will print the configuration of the builder
- push will push the built images to the registry
- --load is optional and will load the image into docker
  - When using --load, only a sinle platform can be specified. An example of overriding the platform for 'linux/amd64' is `--set default.platform=linux/amd64`
  - Is no longer an issue if using containerd as the backend (https://www.docker.com/blog/extending-docker-integration-with-containerd/)


# Publishing Versions
The workflow for publishing a new version of the farm device is documented below. The project uses semantic versioning.

## Git Branches
The `main` branch is the latest version of the project. All new code should be merged into this branch.

The `v{major.minor}` branches track the combination of major and minor versions of the project. Each `v{major.minor}` version has its own branch. The `v1.2` branch will track all changes to the `1.2` version of the project. This includes patches and new features.

New features or patches should be created in a new branch. Eg. `feature/temperature_reading_average` or `fix/temperature_reading_bug`. Once the changes are complete, the branch should be merged into the `main` branch and optionally into the `v{major.minor}` branch and tagged with the appropriate version number (eg. `v{major.minor.patch}`).


## Publishing Changes
When a new version is to be published, the following steps should be taken.

The new version can either be a major, minor, or patch version. Determine the appropriate version number that is to be published.

If the version is a patch version change:
1. Create a new branch from either the `main` or `v{major.minor}`branch with an appropriate name. eg. `fix/temperature_reading_bug`
2. Make the necessary changes to the code.
3. Update the `CHANGELOG.md` file with the increased patch version, changes made, and any update instructions.
4. Merge the branch into the `main` branch
    1. Build the docker containers with the `latest` tag and push them to the registry.
5. Optionally, merge the branch into the appropriate `v{major.minor}` branches.
    1. Create a tag with the new version number (eg. `v{major.minor.patch}`).
    2. Build the docker containers with the required tags (eg. `v{major.minor}` and `v{major.minor.patch}`) and push to the registry.
6. Delete the feature or fix branch.

If the version is a major or minor version change:
1. Create a new branch from the `main` branch following the semanting versioning rules. eg. `v{major.minor}`
2. Update the `CHANGELOG.md` file with the increased version number, changes made, and any update instructions.
3. From that point on, the new branch will track this major version and the `main` branch will continue to track the latest version.
4. Build the docker containers with the new tag and push them to the registry.
4. Add patch or fix versions to the `v{major.minor}` branch as needed (described above).
