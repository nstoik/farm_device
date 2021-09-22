"""Main celery module."""
import logging
import time
from datetime import timedelta

import schedule
from celery import Celery

LOGGER = logging.getLogger("fd.celery_runner")

app = Celery()

app.config_from_object("fd_device.settings:CeleryConfig")

# app.send_task("device.create", args=[{"Hello": "World"}])


def job():
    """Dummy function."""
    print("Hello")


schedule.every(5).seconds.until(timedelta(seconds=30)).do(job)


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
