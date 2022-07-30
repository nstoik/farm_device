"""The main module for the fd_device."""
import logging
import time
from logging.handlers import RotatingFileHandler
from multiprocessing import Process

from multiprocessing_logging import install_mp_handler

from fd_device.celery_runner import run_scheduled_tasks
from fd_device.database.base import get_session

from .settings import get_config
from .startup import check_if_setup, get_rabbitmq_address

# from fd_device.device.service import run_connection


def configure_logging(config):
    """Configure the logging for the application."""

    logger = logging.getLogger("fd")
    logfile_path = config.LOG_FILE
    log_level = config.LOG_LEVEL

    logger.setLevel(log_level)
    logger.propagate = False

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    file_handler = RotatingFileHandler(
        logfile_path, mode="a", maxBytes=1024 * 1024, backupCount=10
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Install a stream handler to send logs to stdout for docker logs
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    install_mp_handler(logger=logger)

    return logger


def main():
    """The main loop of the application."""

    config = get_config()
    logger = configure_logging(config)
    session = get_session()

    if not check_if_setup(logger, session):
        logger.error("System has not been setup. Please run first time setup command")
        time.sleep(5)
        return

    if not get_rabbitmq_address(logger, session):
        logger.error("No address for rabbitmq server found")
        time.sleep(5)
        return

    # device_connection = Process(target=run_connection)
    scheduler_process = Process(target=run_scheduled_tasks)

    # device_connection.start()
    scheduler_process.start()

    try:
        # device_connection.join()
        scheduler_process.join()
    except KeyboardInterrupt:
        logger.warning("Keyboard interrupt in main process")

        time.sleep(1)
        # device_connection.terminate()
        # device_connection.join()

        scheduler_process.terminate()
        scheduler_process.join()

    return


if __name__ == "__main__":
    main()
