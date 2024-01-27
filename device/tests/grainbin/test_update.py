"""grainbin.update module tests."""
import datetime

import pytest
from pytest_mock import MockerFixture

from fd_device.grainbin.update import (
    get_average_temperature,
    get_grainbin_updates,
    get_indivudual_grainbin_update,
)
from fd_device.settings import get_config

from ..factories import GrainbinFactory

CONFIG = get_config()


@pytest.mark.usefixtures("tables")
class TestGetIndividualGrainbinUpdate:
    """Test the get_individual_grainbin_update function."""

    # Sensor data for testing
    test_sensor_list_1 = ["28.CC9A290D0000", "28.BC9A290D0000", "28.BBE5290D0000"]
    test_sensor_data_1 = [
        {"temperature": "22.1875", "temphigh": "1", "templow": "1"},
        {"temperature": "22.625", "temphigh": "1", "templow": "2"},
        {"temperature": "22.4375", "temphigh": "1", "templow": "3"},
    ]
    test_grainbin_update_1 = {
        "created_at": datetime.datetime(2024, 1, 27, 5, 29, 20, 264830),
        "name": "Test Grainbin0",
        "bus_number": 0,
        "bus_number_string": "bus.0",
        "sensor_names": ["28.CC9A290D0000", "28.BC9A290D0000", "28.BBE5290D0000"],
        "sensor_data": [
            {
                "temperature": "22.1875",
                "temphigh": "1",
                "templow": "1",
                "sensor_name": "28.CC9A290D0000",
            },
            {
                "temperature": "22.625",
                "temphigh": "1",
                "templow": "2",
                "sensor_name": "28.BC9A290D0000",
            },
            {
                "temperature": "22.4375",
                "temphigh": "1",
                "templow": "3",
                "sensor_name": "28.BBE5290D0000",
            },
        ],
        "average_temp": "22.4167",
    }

    test_grainbin_update_2 = {
        "created_at": datetime.datetime(2024, 1, 27, 5, 29, 20, 264830),
        "name": "Test Grainbin1",
        "bus_number": 1,
        "bus_number_string": "bus.1",
        "sensor_names": ["28.CC9A290D0000", "28.BC9A290D0000"],
        "sensor_data": [
            {
                "temperature": "22.1875",
                "temphigh": "2",
                "templow": "1",
                "sensor_name": "28.CC9A290D0000",
            },
            {
                "temperature": "22.625",
                "temphigh": "2",
                "templow": "2",
                "sensor_name": "28.BC9A290D0000",
            },
        ],
        "average_temp": "22.4062",
    }

    @staticmethod
    def test_get_average_temperature():
        """Test the get_average_temperature function."""

        test_temperatures = ["22.1875", "22.625", "22.4375"]

        avg_temperature = get_average_temperature(test_temperatures)

        assert isinstance(avg_temperature, str)
        assert avg_temperature == "22.4167"

    @staticmethod
    def test_get_average_temperature_percision():
        """Test the get_average_temperature function with different percision."""

        test_temperatures = ["22.1875", "22.625", "22.4375"]

        avg_temperature = get_average_temperature(test_temperatures, percision=2)

        assert isinstance(avg_temperature, str)
        assert avg_temperature == "22.42"

    @staticmethod
    def test_get_average_temperature_empty():
        """Test the get_average_temperature function with an empty list."""

        test_temperatures = []

        avg_temperature = get_average_temperature(test_temperatures)

        assert isinstance(avg_temperature, str)
        assert avg_temperature == "N/A"

    @staticmethod
    def test_get_individual_grainbin_update(mocker: MockerFixture):
        """Test the get_individual_grainbin_update function."""

        mocker.patch(
            "fd_device.grainbin.update.get_all_sensors_of_bus",
            return_value=TestGetIndividualGrainbinUpdate.test_sensor_list_1,
        )

        mocker.patch(
            "fd_device.grainbin.update.read_sensor_of_bus",
            side_effect=TestGetIndividualGrainbinUpdate.test_sensor_data_1,
        )

        grainbin = GrainbinFactory()

        individual_update = get_indivudual_grainbin_update(grainbin)

        assert isinstance(individual_update, dict)
        assert isinstance(individual_update["created_at"], datetime.datetime)
        assert individual_update["name"] == grainbin.name
        assert individual_update["bus_number"] == grainbin.bus_number
        assert individual_update["bus_number_string"] == grainbin.bus_number_string
        assert isinstance(individual_update["sensor_names"], list)
        assert isinstance(individual_update["sensor_data"], list)
        assert isinstance(individual_update["average_temp"], str)

    @staticmethod
    def test_get_grainbin_updates(mocker: MockerFixture):
        """Test the get_grainbin_updates function."""

        mocker.patch(
            "fd_device.grainbin.update.get_all_busses",
            return_value=["bus.1", "bus.2"],
        )

        individual_updates = [
            TestGetIndividualGrainbinUpdate.test_grainbin_update_1,
            TestGetIndividualGrainbinUpdate.test_grainbin_update_2,
        ]
        mocker.patch(
            "fd_device.grainbin.update.get_indivudual_grainbin_update",
            side_effect=individual_updates,
        )

        grainbins = GrainbinFactory.create_batch(2)
        grainbins[0].update(bus_number_string="bus.1")
        grainbins[1].update(bus_number_string="bus.2")
        grainbin_update = get_grainbin_updates()

        assert isinstance(grainbin_update, list)
        assert len(grainbin_update) == 2

    @staticmethod
    def test_get_grainbin_updates_with_session(mocker: MockerFixture, dbsession):
        """Test the get_grainbin_updates function with a session."""

        mocker.patch(
            "fd_device.grainbin.update.get_all_busses",
            return_value=["bus.1", "bus.2"],
        )

        individual_updates = [
            TestGetIndividualGrainbinUpdate.test_grainbin_update_1,
            TestGetIndividualGrainbinUpdate.test_grainbin_update_2,
        ]
        mocker.patch(
            "fd_device.grainbin.update.get_indivudual_grainbin_update",
            side_effect=individual_updates,
        )

        grainbins = GrainbinFactory.create_batch(2)
        grainbins[0].update(bus_number_string="bus.1")
        grainbins[1].update(bus_number_string="bus.2")
        grainbin_update = get_grainbin_updates(session=dbsession)

        assert isinstance(grainbin_update, list)
        assert len(grainbin_update) == 2

    @staticmethod
    def test_get_grainbin_updates_no_grainbins(mocker: MockerFixture):
        """Test the get_grainbin_updates function with no grainbins."""

        mocker.patch("fd_device.grainbin.update.get_all_busses")

        grainbin_update = get_grainbin_updates()

        assert isinstance(grainbin_update, list)
        assert len(grainbin_update) == 0
