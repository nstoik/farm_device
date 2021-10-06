"""Control module tests.

TODO: add tests for set_device_name, set_service_state, set_sensor_info
"""
import pytest
from sqlalchemy.orm.exc import NoResultFound

from fd_device.database.system import Hardware, Software
from fd_device.system.control import (
    set_hardware_info,
    set_sensor_info,
    set_software_info,
)


@pytest.mark.usefixtures("tables")
def test_set_sensor_info(dbsession, mocker):
    """Test the set_sensor_info function works."""

    with pytest.raises(NoResultFound):
        dbsession.query(Hardware).one()

    mocked_sensors = [{"name": "sensor_1_name"}, {"name": "sensor_2_name"}]

    mocker.patch(
        "fd_device.system.control.get_connected_sensors",
        return_value=mocked_sensors,
        autospec=True,
    )

    set_sensor_info(interior=1, exterior=2)

    hd = dbsession.query(Hardware).one()

    assert hd.interior_sensor == mocked_sensors[0]
    assert hd.exterior_sensor == mocked_sensors[1]


@pytest.mark.usefixtures("tables")
def test_set_sensor_info_wrong_choices(dbsession, mocker):
    """Test the set_sensor_info function handles incorrect choices."""

    with pytest.raises(NoResultFound):
        dbsession.query(Hardware).one()

    mocked_sensors = [{"name": "sensor_1_name"}, {"name": "sensor_2_name"}]

    mocker.patch(
        "fd_device.system.control.get_connected_sensors",
        return_value=mocked_sensors,
        autospec=True,
    )

    set_sensor_info(interior=3, exterior=4)

    hd = dbsession.query(Hardware).one()

    assert hd.interior_sensor == "no_sensor_selected"
    assert hd.exterior_sensor == "no_sensor_selected"


@pytest.mark.usefixtures("tables")
def test_set_hardware_info(dbsession):
    """Test the set_hardware_info function."""

    set_hardware_info("test_hardware_version", 0)

    hd = dbsession.query(Hardware).one()

    assert hd.hardware_version == "test_hardware_version"
    assert isinstance(hd.device_name, str)
    assert isinstance(hd.serial_number, str)
    assert hd.grainbin_reader_count == 0


@pytest.mark.usefixtures("tables")
def test_set_software_info(dbsession):
    """Test the set_software_info function.

    :param dbsession: pytest fixture for a Sqlalchemy session object
    """

    set_software_info("test_software_version")

    sd = dbsession.query(Software).one()

    assert sd.software_version == "test_software_version"
