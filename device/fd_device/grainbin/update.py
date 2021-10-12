"""Get update objects for the grainbins."""
import datetime
import statistics

from sqlalchemy.orm.session import Session

from fd_device.database.base import get_session
from fd_device.database.device import Grainbin
from fd_device.grainbin.owfs_interface import (
    get_all_busses,
    get_all_sensors_of_bus,
    read_sensor_of_bus,
)


def get_grainbin_info(session: Session = None) -> dict:
    """Get all grainbin information.

    Args:
        session (Session, optional): The database session. Defaults to None.

    Returns:
        dict: All the grainbin information for all connected grainbins.
    """

    close_session = False

    if not session:
        close_session = True
        session = get_session()

    grainbins: list[Grainbin] = session.query(Grainbin).all()
    info: dict = {}
    info["created_at"] = datetime.datetime.now()

    all_busses = get_all_busses()
    info["grainbins"] = all_busses
    grainbins_update_data = []

    for bus in all_busses:
        grainbin_data: dict = {}
        grainbin_data["bus"] = bus
        all_sensors = get_all_sensors_of_bus(bus)
        grainbin_data["sensors"] = all_sensors
        temperature = []
        for sensor in all_sensors:
            sensor_info = read_sensor_of_bus(bus, sensor)
            temperature.append(sensor_info["temperature"])
            grainbin_data[sensor] = sensor_info

        avg_temperature = get_average_temperature(temperature)
        grainbin_data["average_temp"] = avg_temperature
        update_db_avg_temperature(grainbins, bus, avg_temperature)

        grainbins_update_data.append(grainbin_data)

    info["data"] = grainbins_update_data
    session.commit()

    if close_session:
        session.close()

    return info


def update_db_avg_temperature(
    grainbins: list[Grainbin], bus_number: str, avg_temp: str
):
    """Update the average temperture in the database for a given bus number and temperature."""

    for grainbin in grainbins:
        if bus_number.endswith(str(grainbin.bus_number)):
            grainbin.average_temp = avg_temp
            return


def get_average_temperature(temperatures: list, percision: int = 4) -> str:
    """Get the average temperature from a list of temperature strings."""

    avg = round(statistics.mean([float(i) for i in temperatures]), percision)

    return str(avg)


if __name__ == "__main__":
    all_info = get_grainbin_info()

    for item in all_info["data"]:
        for key in item:
            print(f"{key} --- {item[key]}")

    print(all_info)
