"""Tests for the helper functions of the setup_commands module."""
import random

import pytest

from fd_device.cli.manage.setup_commands import initialize_device, initialize_grainbin
from fd_device.database.device import Device
from fd_device.system.control import set_hardware_info, set_software_info


@pytest.mark.usefixtures("tables")
def test_initialize_grainbin():
    """Test the initialize_grainbin function."""

    number_of_grainbins = random.randint(1, 10)

    grainbins = initialize_grainbin("10000000255c26b4", number_of_grainbins)

    assert len(grainbins) == number_of_grainbins


@pytest.mark.usefixtures("tables")
def test_initialize_device_no_hardware_or_software(dbsession):
    """Test the initialize_device function returns if hardware or software not set."""

    initialize_device()

    device = dbsession.query(Device).first()

    assert device is None


@pytest.mark.usefixtures("tables")
def test_initialize_device(dbsession):
    """Test the initialize_device function functions as expected."""

    number_of_grainbins = random.randint(1, 10)

    # set the hardware and software info
    set_hardware_info("TEST_HARDWARE_VERSION", str(number_of_grainbins))
    set_software_info("TEST_SOFTWARE_VERSION")

    initialize_device()

    device = dbsession.query(Device).first()

    assert len(device.grainbins) == number_of_grainbins


@pytest.mark.usefixtures("tables")
def test_initialize_device_twice(dbsession):
    """Test the initialize_device function if ran again.

    Both device and grainbins my be present already, so make
    sure the function can handle that gracefully.
    """

    # initialize the device once.
    number_of_grainbins = random.randint(1, 10)
    set_hardware_info("TEST_HARDWARE_VERSION", str(number_of_grainbins))
    set_software_info("TEST_SOFTWARE_VERSION")
    initialize_device()

    device = dbsession.query(Device).first()
    assert len(device.grainbins) == number_of_grainbins

    # now initialize the device again.
    number_of_grainbins_second_time = random.randint(1, 10)
    set_hardware_info("TEST_HARDWARE_VERSION", str(number_of_grainbins_second_time))
    initialize_device()
    device_second = dbsession.query(Device).first()
    assert len(device_second.grainbins) == number_of_grainbins_second_time
