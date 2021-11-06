"""Main celery module."""
import logging
import time

import schedule
from amqp import exceptions as amqp_exceptions  # type: ignore
from celery import Celery, exceptions
from celery.result import AsyncResult

from fd_device.device.update import get_device_info
from fd_device.grainbin.update import get_grainbin_updates
from fd_device.settings import get_config

LOGGER = logging.getLogger("fd.celery_runner")
CONFIG = get_config()

app = Celery()
app.config_from_object("fd_device.settings:CeleryConfig")


def send_update_to_server(task_name: str, payload, ignore_result: bool = False):
    """Send a payload to a specific task on the server."""

    try:
        LOGGER.debug(f"Sending '{task_name}' to Celery broker")
        result: AsyncResult = app.send_task(
            task_name, args=[payload], ignore_result=ignore_result
        )
        if not ignore_result:
            response = result.get(timeout=CONFIG.SEND_TASK_GET_TIMEOUT)
            LOGGER.debug(f"'{task_name}' task returned: {response}")
            return response
        LOGGER.debug(f"'{task_name}' ignoring result")
        return True
    except exceptions.OperationalError as operational_error:
        LOGGER.error(f"Caught Operational error: {operational_error}")
        return False
    except exceptions.TimeoutError as timeout_error:
        LOGGER.error(f"Caught Timeout error: {timeout_error}")
        return False
    except amqp_exceptions.ConnectionForced as connection_error:
        LOGGER.error(f"Caught Connection error: {connection_error}")
        return False
    except OSError as os_error:
        LOGGER.error(f"Caught OSError: {os_error}")
        return False


def send_device_update():
    """Get and send the device update data."""

    LOGGER.debug("Creating device update")
    info = get_device_info()
    LOGGER.debug("Sending device update")
    send_update_to_server("device.update", info)


def send_grainbin_update():
    """Get and send the grainbin update data."""

    LOGGER.debug("Creating grainbin update")
    info = get_grainbin_updates()
    LOGGER.debug("Sending grainbin update")
    for update in info:
        send_update_to_server("grainbin.update", update)


# set schedule
DEVICE_INTERVAL = CONFIG.SCHEDULER_DEVICE_UPDATE_INTERVAL
GRAINBIN_INTERVAL = CONFIG.SCHEDULER_GRAINBIN_UPDATE_INTERVAL
schedule.every(DEVICE_INTERVAL).minutes.at(":00").do(send_device_update)
schedule.every(GRAINBIN_INTERVAL).minutes.at(":00").do(send_grainbin_update)


def run_scheduled_tasks():
    """Run the scheduled tasks using the 'schedule' package."""

    # always send a device update upon start up (in case the device is new to the server)
    send_device_update()

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

            start = time.time()
            schedule.run_pending()
            end = time.time()
            elapsed_time = end - start
            LOGGER.debug(f"SCHEDULER - took: {elapsed_time} seconds to run")
    except KeyboardInterrupt:
        LOGGER.info("Stopping scheduler")

    LOGGER.info("Scheduler is exiting")
