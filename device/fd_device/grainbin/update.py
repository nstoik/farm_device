"""Get update objects for the grainbins."""
import datetime
import logging
import statistics
from typing import Optional

from sqlalchemy.orm.session import Session

from fd_device.database.database import get_session
from fd_device.database.device import Grainbin
from fd_device.grainbin.owfs_interface import (
    get_all_busses,
    get_all_sensors_of_bus,
    read_sensor_of_bus,
)

LOGGER = logging.getLogger("fd.grainbin.update")


def get_grainbin_updates(session: Optional[Session] = None) -> list:
    """Get all grainbin updates as a list for each grainbin."""

    close_session = False
    if not session:
        close_session = True
        session = get_session()

    all_updates: list = []

    grainbins: list[Grainbin] = session.query(Grainbin).all()

    all_busses = get_all_busses()

    for grainbin in grainbins:
        if grainbin.bus_number_string in all_busses:
            update = get_indivudual_grainbin_update(grainbin)
            all_updates.append(update)
        else:
            LOGGER.warning(
                f"Bus {grainbin.bus_number_string} not currently connected when trying to create update."
            )

    session.commit()
    if close_session:
        session.close()

    return all_updates


def get_indivudual_grainbin_update(grainbin: Grainbin) -> dict:
    """Create and retrieve an update for an individual grainbin."""

    info: dict = {}
    info["created_at"] = datetime.datetime.now()
    info["name"] = grainbin.name
    info["bus_number"] = grainbin.bus_number
    info["bus_number_string"] = grainbin.bus_number_string
    all_sensors = get_all_sensors_of_bus(grainbin.bus_number_string)
    info["sensor_names"] = all_sensors

    temperature = []
    sensor_data = []
    for sensor in all_sensors:
        sensor_info = read_sensor_of_bus(grainbin.bus_number_string, sensor)
        sensor_info["sensor_name"] = sensor
        temperature.append(sensor_info["temperature"])
        sensor_data.append(sensor_info)

    avg_temperature = get_average_temperature(temperature)
    info["sensor_data"] = sensor_data
    info["average_temp"] = avg_temperature
    grainbin.average_temp = avg_temperature

    return info


def get_average_temperature(temperatures: list, percision: int = 4) -> str:
    """Get the average temperature from a list of temperature strings."""

    avg = round(statistics.mean([float(i) for i in temperatures]), percision)

    return str(avg)


if __name__ == "__main__":
    updates = get_grainbin_updates()
    for x in updates:
        print("UPDATE")
        for key in x:
            print(f"{key} --- {x[key]}")
