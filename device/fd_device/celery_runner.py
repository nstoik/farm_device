"""Main celery module."""
import logging
import time

import schedule
from amqp import exceptions as amqp_exceptions  # type: ignore
from celery import Celery, exceptions

from fd_device.device.update import get_device_info
from fd_device.settings import get_config

LOGGER = logging.getLogger("fd.celery_runner")

app = Celery()
app.config_from_object("fd_device.settings:CeleryConfig")


def send_device_update():
    """Get and send the device update data."""

    info = get_device_info()
    try:
        LOGGER.debug("Sending 'device.update' to Celery broker")
        response = app.send_task("device.update", [info]).get(timeout=5)
        LOGGER.debug(f"'device.update' task returned: {response}")
        return response
    except exceptions.OperationalError as operational_error:
        LOGGER.error(f"Caught Operational error: {operational_error}")
        return False
    except exceptions.TimeoutError as timeout_error:
        LOGGER.error(f"Caught Timeout error: {timeout_error}")
        return False
    except amqp_exceptions.ConnectionForced as connection_error:
        LOGGER.error(f"Caught Connection error: {connection_error}")
        return False


# set schedule
DEVICE_INTERVAL = get_config().SCHEDULER_DEVICE_UPDATE_INTERVAL
schedule.every(DEVICE_INTERVAL).minutes.do(send_device_update)


def run_scheduled_tasks():
    """Run the scheduled tasks using the 'schedule' package."""

    try:
        while True:
            idle_seconds = schedule.idle_seconds()

            if idle_seconds is None:
                # no more jobs to run
                LOGGER.warning("No more jobs for scheduler to run")
                break

            if idle_seconds > 0:
                # sleep till the next scheduled job needs to be run
                LOGGER.debug(f"scheduler sleeping for {idle_seconds} seconds.")
                time.sleep(idle_seconds)

            schedule.run_pending()
    except KeyboardInterrupt:
        LOGGER.info("Stopping scheduler")

    LOGGER.info("Scheduler is exiting")
