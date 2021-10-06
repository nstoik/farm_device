"""Update module test."""
import random

import pytest

from fd_device.device.update import get_device_info

from ..factories import DeviceFactory


@pytest.mark.usefixtures("tables")
def test_get_device_info(mocker):
    """Test the get_device_info function."""

    device = DeviceFactory()
    device.interior_sensor = "sensor_1"
    device.exterior_sensor = "sensor_2"
    device.save()

    mocker.patch(
        "fd_device.device.update.temperature",
        return_value=random.uniform(-40, 100),
        autospec=True,
    )

    update = get_device_info()

    assert isinstance(update, dict)
    assert update["data"]["device_id"] == device.device_id
