"""Fixtures for the network module tests."""
# pylint: disable=unused-argument
import pytest

from fd_device.database.system import Interface


@pytest.fixture()
def populate_interfaces(tables):
    """Populate interfaces into the database."""

    interface = Interface("wlan0")
    interface.update(is_active=True, is_for_fm=True, is_external=True, state="dhcp")
