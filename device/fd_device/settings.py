"""Application configuration."""
# pylint: disable=too-few-public-methods

import logging
import os

from environs import Env

env = Env()
env.read_env()


class Config:
    """Base configuration."""

    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
    TEST_DIR = os.path.abspath(os.path.join(PROJECT_ROOT, "tests"))

    PRESENCE_PORT = 5554

    LOG_LEVEL = env.log_level("FD_DEVICE_LOG_LEVEL", default=logging.INFO)
    LOG_FILE = "/logs/farm_device.log"

    # UPDATER_PATH = "/home/pi/farm_monitor/farm_update/update.sh"

    POSTGRES_PASSWORD = env("POSTGRES_PASSWORD", default="farm_device")
    POSTGRES_USER = env("POSTGRES_USER", default="fd")
    POSTGRES_DB = env("POSTGRES_DB", default="farm_device.db")
    POSTGRES_HOST = env("POSTGRES_HOST", default="fd_database")
    SQLALCHEMY_DATABASE_URI = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"
    # SQLALCHEMY_DATABASE_URI = "postgresql://fd:farm_device@fd_database/farm_device.db"

    RABBITMQ_USER = "fd"
    RABBITMQ_PASSWORD = "farm_monitor"
    RABBITMQ_VHOST = "farm_monitor"

    RABBITMQ_HOST_ADDRESS = env.str("RABBITMQ_HOST_ADDRESS", default=None)

    # Scheduler settings
    SEND_TASK_GET_TIMEOUT = 5
    # How often to send the device update. Every x minutes
    SCHEDULER_DEVICE_UPDATE_INTERVAL = 60
    # How often to send the grainbin update. Every x minutes
    SCHEDULER_GRAINBIN_UPDATE_INTERVAL = 30


class DevConfig(Config):
    """Development configuration."""

    DEBUG = True
    LOG_LEVEL = env.log_level("FD_DEVICE_LOG_LEVEL", default=logging.DEBUG)


class ProdConfig(Config):
    """Production configuration."""

    DEBUG = False
    LOG_LEVEL = env.log_level("FD_DEVICE_LOG_LEVEL", default=logging.INFO)


class TestConfig(Config):
    """Test configuration."""

    DEBUG = True
    TESTING = True

    SQLALCHEMY_DATABASE_URI = "sqlite:////tmp/fd_device_test_db.sqlite"


class CeleryConfig:
    """Celery configuration."""

    # Broker settings.
    # broker_url = "amqp://fd:farm_monitor@10.10.1.204/farm_monitor"
    broker_url = f"amqp://{Config.RABBITMQ_USER}:{Config.RABBITMQ_PASSWORD}@{Config.RABBITMQ_HOST_ADDRESS}/{Config.RABBITMQ_VHOST}"  # noqa=E501

    # List of modules to import when the Celery worker starts.
    # imports = ('fm_server.device.tasks',)

    # Using the database to store task state and results.
    result_backend = "rpc://"

    # set the broker transport options.
    # confirm_publish 'True' waits until the publish is confirmed.
    # the rest of the settings deal with timeouts.
    # retry 5 times, starting at 0 seconds and incrementing 1 second
    # each time, up until a max of 30 seconds
    broker_transport_options = {
        "confirm_publish": True,
        "max_retries": 5,
        "interval_start": 0,
        "interval_step": 1,
        "interval_max": 30,
    }

    broker_pool_limit = 0


def get_config(override_default=None):
    """Return the Config option based on environment variables.

    If override_default is passed, that configuration is used instead.
    If there is no match or nothing set then the environment defaults to 'dev'.
    """

    if override_default is None:
        environment = env.str("FD_DEVICE_CONFIG", default="dev")
    else:
        environment = override_default

    if environment == "dev":
        return DevConfig
    if environment == "prod":
        return ProdConfig
    if environment == "test":
        return TestConfig
    return DevConfig
