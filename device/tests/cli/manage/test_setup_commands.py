"""Test the setup_commands module."""
import pytest
from click.testing import CliRunner

from fd_device.cli.manage.setup_commands import first_setup
from fd_device.database.device import Device
from fd_device.database.system import SystemSetup


@pytest.mark.usefixtures("tables")
def test_first_setup_execution():
    """Test that first_setup starts and executes."""

    runner = CliRunner()
    result = runner.invoke(first_setup)

    assert "First time setup" in result.output


@pytest.mark.usefixtures("tables")
def test_first_setup_already_completed(dbsession):
    """Test that the cli command detects if setup already done."""

    # explicitly set the first_setup to true.
    system = SystemSetup()
    system.first_setup = True
    system.save(dbsession)

    runner = CliRunner()
    result = runner.invoke(first_setup, input="N\n")

    assert not result.exception
    assert "Setup has already been run" in result.output


@pytest.mark.usefixtures("tables")
def test_first_setup_standalone_no_to_all():
    """Test standalone flag passed in."""

    runner = CliRunner()
    result = runner.invoke(first_setup, args="--standalone", input="N\nN\nN\nN\nN\n")

    assert "Do you want to change the device name?" in result.output
    assert not result.exception


@pytest.mark.usefixtures("tables")
def test_first_setup_no_to_all():
    """Test without standalone flag."""

    runner = CliRunner()
    # answer yes to the first question (is this standalone config?)
    result = runner.invoke(first_setup, input="y\nN\nN\nN\nN\nN\n")

    assert "Is this a standalone configuration?" in result.output
    assert "Do you want to change the device name?" in result.output
    assert "Do you want to set hardware informations?" in result.output
    assert "Do you want to set the sensor information" in result.output
    assert "Do you want to set the software information?" in result.output
    assert "Do you want to set details for the interfaces?" in result.output
    assert not result.exception


@pytest.mark.usefixtures("tables")
def test_first_setup_not_standalone_text():
    """Test not standalone setting all the required information.

    This runs through all branches possible without having the hardware
    attached to the fd_device.
    """

    runner = CliRunner()
    input_text = "n\nY\n\n1\n\nY\n0.1\n"
    result = runner.invoke(first_setup, input=input_text)

    assert "Is this a standalone configuration?" in result.output
    assert "Do you want to set hardware informations?" in result.output
    assert "Enter the hardware version" in result.output
    assert "Enter the number of grainbin reader chips on the board" in result.output
    assert "Do you want to set the sensor information" in result.output
    assert "Do you want to set the software information?" in result.output
    assert "Enter the software version" in result.output
    assert not result.exception


@pytest.mark.usefixtures("tables")
def test_first_setup_not_standalone_db(dbsession):
    """Test not standalone and confirm the db is updated."""

    runner = CliRunner()
    input_text = "n\nY\n\n1\n\nY\n0.1\n"
    result = runner.invoke(first_setup, input=input_text)

    device = dbsession.query(Device).one()

    assert not result.exception
    assert isinstance(device.device_id, str)
    assert device.hardware_version == "pi3_0001"
    assert device.grainbin_count == 1
    assert device.software_version == "0.1"
    assert device.interior_sensor is None
    assert device.exterior_sensor is None


@pytest.mark.usefixtures("tables")
def test_first_setup_setup_hardware_information():
    """Test that setting the hardware information works."""

    runner = CliRunner()
    result = runner.invoke(first_setup, input="y\nN\ny\n\n2\nN\ny\n0.1\n\n")

    # answered yes
    assert "Is this a standalone configuration?" in result.output
    # answered NO
    assert "Do you want to change the device name?" in result.output
    # answered yes and accepted default of pi3_0001. Entered 2 for number of grainbin reader chips
    assert "Do you want to set hardware informations?" in result.output
    assert "Enter the hardware version [pi3_0001]:" in result.output
    assert "Enter the number of grainbin reader chips on the board [0]" in result.output
    # answered No
    assert "Do you want to set the sensor information" in result.output
    # answered yes and entered 0.1
    assert "Do you want to set the software information?" in result.output
    # answered no
    assert "Do you want to set details for the interfaces?" in result.output
    assert not result.exception


@pytest.mark.usefixtures("tables")
def test_first_setup_setup_temp_sensors(mocker):
    """Test that setting the hardware information works."""

    mocked_sensors = [
        {"name": "sensor_1_name", "temperature": 22.38},
        {"name": "sensor_2_name", "temperature": 22.19},
    ]

    mocker.patch(
        "fd_device.cli.manage.setup_commands.get_connected_sensors",
        return_value=mocked_sensors,
        autospec=True,
    )

    runner = CliRunner()
    result = runner.invoke(first_setup, input="y\nN\ny\n\n2\ny\n\n\ny\n0.1\n\n")

    # answered yes
    assert "Is this a standalone configuration?" in result.output
    # answered NO
    assert "Do you want to change the device name?" in result.output
    # answered yes and accepted default of pi3_0001. Entered 2 for number of grainbin reader chips
    assert "Do you want to set hardware informations?" in result.output
    assert "Enter the hardware version [pi3_0001]:" in result.output
    assert "Enter the number of grainbin reader chips on the board [0]" in result.output
    # answered yes
    assert "Do you want to set the sensor information" in result.output
    assert "Current sensor information:" in result.output
    assert "1. Sensor: sensor_1_name Temperature: 22.38" in result.output
    assert "2. Sensor: sensor_2_name Temperature: 22.19" in result.output
    # answered default 1 and 2 for sensor selection
    assert "Select which sensor is the internal temperature [1]:" in result.output
    assert "Select which sensor is the external temperature [2]:" in result.output
    # answered yes and entered 0.1
    assert "Do you want to set the software information?" in result.output
    # answered no
    assert "Do you want to set details for the interfaces?" in result.output
    assert not result.exception
