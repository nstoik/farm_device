"""Test device models."""
import datetime as dt

import pytest

from fd_device.database.device import Connection, Device, Grainbin

from .factories import DeviceFactory, GrainbinFactory


@pytest.mark.usefixtures("tables")
class TestConnection:
    """Connection model tests."""

    @staticmethod
    def test_create_connection_object():
        """Create a Connection instance."""

        connection = Connection()
        connection.save()

        assert connection.last_updated is None
        assert isinstance(connection.first_connected, dt.datetime)
        assert not bool(connection.is_connected)

    @staticmethod
    def test_update_connection_object():
        """Create and update a Connection instance."""

        connection = Connection()
        connection.save()

        connection.is_connected = True
        connection.save()

        assert isinstance(connection.last_updated, dt.datetime)
        assert bool(connection.is_connected)


@pytest.mark.usefixtures("tables")
class TestDevice:
    """Device model tests."""

    @staticmethod
    def test_create_device_object():
        """Create a Device instance."""

        device = Device(device_id="TEST01")
        device.save()

        assert device.__repr__() == "<Device: device_id=TEST01>"
        assert device.device_id == "TEST01"
        assert device.interior_sensor == "null"
        assert device.exterior_sensor == "null"

    @staticmethod
    def test_get_device_by_id():
        """Test retrieving a device by its ID."""

        device = Device(device_id="TEST01")
        device.save()

        retrieved = Device.get_by_id(device.id)

        assert device.id == retrieved.id

    @staticmethod
    def test_device_factory():
        """Test DeviceFactory."""

        device = DeviceFactory()
        device.save()

        retrieved = Device.get_by_id(device.id)

        assert device.id == retrieved.id

    @staticmethod
    def test_device_properties():
        """Test all Device properties."""

        device = DeviceFactory()
        device.save()

        assert device.hardware_version is None
        assert device.software_version is None
        assert isinstance(device.creation_time, dt.datetime)
        assert isinstance(device.last_updated, dt.datetime)
        assert device.interior_sensor == "null"
        assert device.exterior_sensor == "null"
        assert device.interior_temp is None
        assert device.exterior_temp is None
        assert device.grainbin_count == 0
        assert device.grainbins == []


@pytest.mark.usefixtures("tables")
class TestGrainbin:
    """Grainbin model tests."""

    @staticmethod
    def test_create_grainbin():
        """Create a grainbin instance."""
        device = DeviceFactory()
        device.save()

        grainbin = Grainbin(name="TestGrainbin", bus_number=1, device_id=device.id)
        grainbin.save()

        assert grainbin.device_id == device.id
        assert grainbin.bus_number == 1

    @staticmethod
    def test_get_grainbin_by_id():
        """Test retrieving a grainbin by its ID."""
        device = DeviceFactory()
        device.save()

        grainbin = Grainbin(name="TestGrainbin", bus_number=1, device_id=device.id)
        grainbin.save()

        retrieved = Grainbin.get_by_id(grainbin.id)

        assert grainbin.id == retrieved.id

    @staticmethod
    def test_grainbin_factory():
        """Test GrainbinFactory."""

        grainbin = GrainbinFactory()
        grainbin.save()

        retrieved = Grainbin.get_by_id(grainbin.id)
        device = Device.get_by_id(grainbin.device_id)

        assert grainbin.id == retrieved.id
        assert isinstance(grainbin.device_id, int)
        assert isinstance(device, Device)

    @staticmethod
    def test_grainbin_properies():
        """Test all Grainbin properties."""

        grainbin = GrainbinFactory()
        grainbin.save()

        assert grainbin.name.startswith("Test Grainbin")
        assert isinstance(grainbin.bus_number, int)
        assert isinstance(grainbin.creation_time, dt.datetime)
        assert isinstance(grainbin.last_updated, dt.datetime)
        assert grainbin.average_temp == "unknown"
