# -*- coding: utf-8 -*-
"""Click commands."""
import os
import sys
from glob import glob
from subprocess import PIPE, call, run
from typing import List

import click

from fd_device.settings import get_config

config = get_config()  # pylint: disable=invalid-name
APP_DIR = config.APP_DIR
PROJECT_ROOT = config.PROJECT_ROOT
TEST_PATH = os.path.join(PROJECT_ROOT, "tests")
MAX_DEPTH_RECUR = 50
"""The maximum depth to reach while recursively exploring sub folders."""


def get_files_from_dir(path, recursive=True, depth=0, file_ext=".py"):
    """Retrieve the list of files from a folder.

    @param path: file or directory where to search files
    @param recursive: if True will search also sub-directories
    @param depth: if explore recursively, the depth of sub directories to follow
    @param file_ext: the files extension to get. Default is '.py'
    @return: the file list retrieved. if the input is a file then a one element list.
    """
    file_list = []
    if os.path.isfile(path) or path == "-":
        return [path]
    if path[-1] != os.sep:
        path = path + os.sep
    for f in glob(path + "*"):
        if os.path.isdir(f):
            if depth < MAX_DEPTH_RECUR:  # avoid infinite recursive loop
                file_list.extend(get_files_from_dir(f, recursive, depth + 1))
            else:
                continue
        elif f.endswith(file_ext):
            file_list.append(f)
    return file_list


def get_root_files_and_directories() -> List[str]:
    """Get the root .python files and root directories.

    Returns:
        List[str]: A list of strings of directories and Python files.
    """
    skip = [
        "requirements",
        "migrations",
        "__pycache__",
        "fd_device.egg-info",
        "build",
    ]
    root_files = glob(PROJECT_ROOT + "/*.py")
    root_directories = [
        os.path.join(PROJECT_ROOT, name)
        for name in next(os.walk(PROJECT_ROOT))[1]
        if not name.startswith(".")
    ]
    files_and_directories = [
        arg for arg in root_files + root_directories if not arg.endswith(tuple(skip))
    ]

    return files_and_directories


@click.command()
@click.option(
    "-c",
    "--coverage",
    default=False,
    is_flag=True,
    help="Run tests with coverage",
)
@click.option(
    "-f",
    "--filename",
    default=None,
    help="Run a specific test file. eg. 'tests/test_forms.py'",
)
@click.option(
    "-k",
    "--function",
    default=None,
    help="Run tests by name eg. 'test_get_by_id' or 'test_get_by_id or test_validate_success'",
)
def test(coverage, filename, function):
    """Run the tests."""

    if filename:
        pytest_args = [filename, "--verbose"]
    else:
        pytest_args = [TEST_PATH, "--verbose"]
    if function:
        pytest_args.extend(["-k", function])
    if coverage:
        pytest_args.extend(["--cov", APP_DIR])
        pytest_args.extend(["--cov-report", "term-missing:skip-covered"])

    # Get the virtual environment to the path for subprocess calls
    pipenv_path = run(["pipenv", "--venv"], check=True, stdout=PIPE)
    pipenv_path = pipenv_path.stdout.decode().replace("\n", "")
    pipenv_path = os.path.join(pipenv_path, "bin")

    def execute_tool(description, pipenv_path_with_bin, *args):
        """Execute a checking tool with its arguments."""

        # Add the virtual environment to the path for subprocess calls
        my_env = os.environ.copy()
        my_env["PATH"] = os.pathsep.join([pipenv_path_with_bin, my_env["PATH"]])

        command_line = list(args)
        click.echo(f"{description}: {' '.join(command_line)}")
        rv = call(command_line, env=my_env)
        return rv

    previous_env = os.getenv("FD_DEVICE_CONFIG", default="dev")
    os.environ["FD_DEVICE_CONFIG"] = "test"
    rv = execute_tool("Run pytest", pipenv_path, "pytest", *pytest_args)
    os.environ["FD_DEVICE_CONFIG"] = previous_env

    sys.exit(rv)


@click.command()
@click.option(
    "-f",
    "--fix-imports",
    default=True,
    is_flag=True,
    help="Fix imports using isort, before linting",
)
@click.option(
    "-c",
    "--check",
    default=False,
    is_flag=True,
    help="Don't make any changes to files, just confirm they are formatted correctly",
)
def lint(fix_imports, check):
    """Lint and check code style with black, flake8 and isort."""

    files_and_directories = get_root_files_and_directories()

    # Get the virtual environment to the path for subprocess calls
    pipenv_path = run(["pipenv", "--venv"], check=True, stdout=PIPE)
    pipenv_path = pipenv_path.stdout.decode().replace("\n", "")
    pipenv_path = os.path.join(pipenv_path, "bin")
    my_env = os.environ.copy()
    my_env["PATH"] = os.pathsep.join([pipenv_path, my_env["PATH"]])

    def execute_tool(description, *args):
        """Execute a checking tool with its arguments."""
        command_line = list(args) + files_and_directories
        click.echo(f"{description}: {' '.join(command_line)}")

        rv = call(command_line, env=my_env)
        if rv != 0:
            sys.exit(rv)

    isort_args = ["--profile", "black"]
    black_args = ["--diff"]
    mypy_args = ["--warn-unused-ignores", "--show-error-codes"]
    pylint_args = ["--load-plugins", ""]
    if check:
        isort_args.append("--check")
        black_args.append("--check")
        # mypy_args.append("--check")
    if fix_imports:
        execute_tool("Fixing import order", "isort", *isort_args)
    execute_tool("Formatting style", "black", *black_args)
    execute_tool("Checking code style", "flake8")
    execute_tool("Checking for code errors", "pylint", *pylint_args)
    execute_tool("Checking static types", "mypy", *mypy_args)
