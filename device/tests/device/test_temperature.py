"""Temperature module tests."""
import random

from fd_device.device.temperature import get_connected_sensors, temperature


def test_temperature(mocker):
    """Test the temperature function."""

    mocker.patch(
        "fd_device.device.temperature._read_temperature",
        return_value=random.uniform(-40, 100),
        autospec=True,
    )

    value = temperature("nonexistent_filename")

    assert isinstance(value, float)


def test_temperature_no_decimal(mocker):
    """Test the temperature function rounds correctly."""

    mocker.patch(
        "fd_device.device.temperature._read_temperature",
        return_value=random.uniform(-40, 100),
        autospec=True,
    )

    value = temperature("nonexistent_filename", percision=None)

    assert isinstance(value, int)


def test_temperature_undefined(mocker):
    """Test the temperature function handles undefined temperature."""

    mocker.patch(
        "fd_device.device.temperature._read_temperature",
        return_value="U",
        autospec=True,
    )

    value = temperature("nonexistent_filename")

    assert value == "U"


def test_get_connected_sensors(mocker):
    """Test the get_connected_sensors function with default entries."""

    mocked_sensors = ["sensor_1_name", "sensor_2_name"]

    mocker.patch(
        "fd_device.device.temperature._get_sensors",
        return_value=mocked_sensors,
        autospec=True,
    )

    sensors = get_connected_sensors()

    assert isinstance(sensors, list)
    assert len(sensors) == 2
    assert sensors[0]["name"] == mocked_sensors[0]


def test_get_connected_sensors_with_temp(mocker):
    """Test the get_connected_sensors function and getting the temperature."""

    mocked_sensors = ["sensor_1_name", "sensor_2_name"]

    mocker.patch(
        "fd_device.device.temperature._get_sensors",
        return_value=mocked_sensors,
        autospec=True,
    )

    mocker.patch(
        "fd_device.device.temperature._read_temperature",
        return_value=random.uniform(-40, 100),
        autospec=True,
    )

    sensors = get_connected_sensors(values=True)

    assert isinstance(sensors[0]["temperature"], float)
