"""Test system models."""
import datetime as dt

import pytest

from fd_device.database.system import Hardware, Interface, Software, SystemSetup, Wifi


@pytest.mark.usefixtures("tables")
class TestSystemSetup:
    """SystemSetup model tests."""

    @staticmethod
    def test_create_systemsetup():
        """Create a SystemSetup instance."""

        system_setup = SystemSetup.create()

        assert not bool(system_setup.first_setup)
        assert isinstance(system_setup.first_setup_time, dt.datetime)
        assert bool(system_setup.standalone_configuration)

    @staticmethod
    def test_get_system_setup_by_id():
        """Retrieve a SystemSetup instance by id."""

        system_setup = SystemSetup.create()

        retrieved = SystemSetup.get_by_id(system_setup.id)
        assert retrieved.id == system_setup.id


@pytest.mark.usefixtures("tables")
class TestInterface:
    """Interface model tests."""

    @staticmethod
    def test_create_interface():
        """Create a Interface instance."""
        interface = Interface.create(interface="eth0")

        assert interface.interface == "eth0"
        assert bool(interface.is_active)
        assert not bool(interface.is_for_fm)
        assert not bool(interface.is_external)
        assert interface.state is None
        assert interface.credentials == []

    @staticmethod
    def test_interface_get_by_id():
        """Retrieve an interface by the id."""
        interface = Interface.create(interface="eth0")

        retrieved = Interface.get_by_id(interface.id)
        assert retrieved.id == interface.id


@pytest.mark.usefixtures("tables")
class TestWifi:
    """WiFi model tests."""

    @staticmethod
    def test_create_wifi():
        """Create a WiFi instance."""
        wifi = Wifi.create()

        assert wifi.name == "FarmMonitor"
        assert wifi.password == "raspberry"
        assert wifi.mode == "wpa"
        assert wifi.interface_id is None
        assert wifi.interface is None

    @staticmethod
    def test_create_wifi_with_interface():
        """Create a WiFi instance with an interface."""
        interface = Interface.create(interface="eth0")

        wifi = Wifi.create()
        wifi.update(interface=interface)

        assert wifi.interface == interface
        assert wifi.interface_id == interface.id

    @staticmethod
    def test_wifi_get_by_id():
        """Test retrieving a WiFi instance by id."""
        wifi = Wifi.create()

        retrieved = Wifi.get_by_id(wifi.id)

        assert retrieved.id == wifi.id


@pytest.mark.usefixtures("tables")
class TestHardware:
    """Hardware model tests."""

    @staticmethod
    def test_create_hardware():
        """Create a Hardware instance."""
        hardware = Hardware.create()

        assert hardware.device_name is None
        assert hardware.hardware_version is None
        assert hardware.serial_number is None
        assert hardware.interior_sensor is None
        assert hardware.exterior_sensor is None
        assert hardware.grainbin_reader_count == 0

    @staticmethod
    def test_hardware_get_by_id():
        """Retrieve a Hardware instance by the id."""
        hardware = Hardware.create()

        retrieved = Hardware.get_by_id(hardware.id)
        assert retrieved.id == hardware.id


@pytest.mark.usefixtures("tables")
class TestSoftware:
    """Software model tests."""

    @staticmethod
    def test_create_software():
        """Create a Software instance."""
        software = Software.create()

        assert software.software_version is None
        assert software.software_version_last is None

    @staticmethod
    def test_software_get_by_id():
        """Retrieve a Software instance by the id."""
        software = Software.create()

        retrieved = Software.get_by_id(software.id)
        assert retrieved.id == software.id
