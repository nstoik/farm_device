"""Interface with owfs to read connected sensor temperatures."""
import logging
from typing import Union

import requests
from bs4 import BeautifulSoup

LOGGER = logging.getLogger("fd.grainbin.owfs_interface")


def fetch_and_parse_page(url: str) -> Union[list[list[str]], None]:
    """Fetch a page from the given url parse the result into a list.

    The parsing is designed specifically for the layout of the OWFS
    HTTPD pages.
    """
    page = requests.get(url)

    if page.status_code != 200:
        LOGGER.error(f"Error fetching page from fd_1wire. URL is: {url}")
        return None

    data = []
    soup = BeautifulSoup(page.text, "html.parser")
    tables = soup.find_all("table")
    if not tables:
        return []
    # we care about the rows in second table
    rows = tables[1].find_all("tr")
    for row in rows:
        cols = row.find_all("td")
        col_as_list = []
        for col in cols:
            # parse a form element if needed by getting the value from the
            # input tag where the type is 'TEXT'
            form = col.find("form")
            if form:
                for tag in form.find_all("input"):
                    if tag["type"] == "TEXT":
                        col_as_list.append(tag["value"])
            else:
                col_as_list.append(col.get_text())
        data.append(col_as_list)

    return data


def get_all_busses(ignore_all_bus=True) -> list[str]:
    """Get all busses and return them as a list.

    Args:
        ignore_all_bus (str, optional, default = True): Whether or
        not to exclude the all bus. The all bus includes every other bus and sensor.

    Returns:
        list[str]: all the connected bus names in the form of 'bus.X' where X is an integer
    """

    url = "http://fd_1wire:2121"

    data = fetch_and_parse_page(url)

    list_of_buses = []

    if data:
        for row in data:
            if row[0].startswith("bus"):
                list_of_buses.append(row[1])

    if ignore_all_bus:
        list_of_buses.remove("bus.0")
    return sorted(list_of_buses)


def get_all_sensors_of_bus(bus_name: str) -> list[str]:
    """Get all sensors of a given bus."""

    base_url = "http://fd_1wire:2121"

    url = base_url + f"/{bus_name}"

    data = fetch_and_parse_page(url)

    list_of_sensors = []

    if data:
        for row in data:
            if row[0].startswith("28."):
                list_of_sensors.append(row[1])
    return list_of_sensors


def read_sensor_of_bus(bus_name: str, sensor: str) -> dict:
    """Get all sensors of a given bus."""

    base_url = "http://fd_1wire:2121"

    url = base_url + f"/{bus_name}/{sensor}"

    data = fetch_and_parse_page(url)

    sensor_data = {}

    if data:
        for row in data:
            # temperature
            if row[0] == "temperature":
                sensor_data["temperature"] = row[1]
            # cable number
            elif row[0] == "temphigh":
                sensor_data["temphigh"] = row[1]
            # sensor number
            elif row[0] == "templow":
                sensor_data["templow"] = row[1]
    return sensor_data


if __name__ == "__main__":
    all_busses = get_all_busses()
    print(all_busses)

    for bus in all_busses:
        all_sensors = get_all_sensors_of_bus(bus)
        print(all_sensors)
        for my_sensor in all_sensors:
            print(read_sensor_of_bus(bus, my_sensor))
