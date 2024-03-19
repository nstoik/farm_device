# FD Device Device repo

## Vscode Dev Container

When the dev container is first built, you will need to configure the virtual environment inside the container after setting it up

```bash
cd device
pipenv install --dev
```


Then you may be prompted to select a python interpreter and/or reload the window for some of the python extensions to work properly. This only needs to be done when the dev container is rebuilt.

The installation of the dependencies and the setup of the virtual environment could be done automatically using a dockerfile step, but it is commented out to help speed up the dev container build time.


## Commands
The available app commands are:
- ```pipenv shell``` - start the virtual environment
- ```pipenv install``` - install dependencies
- ```pipenv install --dev``` - install dev dependencies
- ```pipenv run {command}``` - run a command in the virtual environment
- ```fd_device``` - commands for the device

To see all available commands type: `fd_device`

```bash
> cd device
> pipenv shell
> pipenv install --dev
> fd_device
Usage: fd_device [OPTIONS] COMMAND [ARGS]...

  Entry point for CLI.

Options:
  --help  Show this message and exit.

Commands:
  database     Command group for database commands.
  first-setup  First time setup.
  lint         Lint and check code style with black, flake8 and isort.
  run          Run the server.
  test         Run the tests.
```



## Docker startup command
The startup script [`start.sh`](./start.sh) is used to start the application. It
waits for the database to be ready, applies any migrations, and then starts the application using the `fd_device run` command.

The `start.sh` script is the entrypoint for the docker container.
