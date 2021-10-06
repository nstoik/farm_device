"""Update module test."""
import pytest

from fd_device.device.update import get_device_info

from ..factories import DeviceFactory


@pytest.mark.usefixtures("tables")
def test_get_device_info():
    """Test the get_device_info function."""

    device = DeviceFactory()
    device.interior_sensor = "sensor_1"
    device.exterior_sensor = "sensor_2"
    device.save()

    update = get_device_info()

    assert isinstance(update, dict)
    assert update["data"]["device_id"] == device.device_id
