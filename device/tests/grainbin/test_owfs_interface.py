"""OWFS interface module tests."""
from fd_device.grainbin.owfs_interface import (
    fetch_and_parse_page,
    get_all_busses,
    get_all_sensors_of_bus,
    read_sensor_of_bus,
)
from fd_device.settings import get_config

CONFIG = get_config()


def test_fetch_and_parse_page(mocker):
    """Test the fetch_and_parse_page function."""

    with open(f"{CONFIG.TEST_DIR}/grainbin/test_root_owfs_page.txt") as f:
        text_as_list = f.readlines()
        test_text = "/n".join(text_as_list)

    mocker.patch(
        "fd_device.grainbin.owfs_interface.requests.get",
        return_value=mocker.Mock(status_code=200, text=test_text),
        autospec=True,
    )

    data = fetch_and_parse_page("test_page")

    assert isinstance(data, list)
    assert len(data) == 15


def test_fetch_and_parse_page_not_200(mocker):
    """Test the fetch_and_parse_page function returns None if not 200."""

    mocker.patch(
        "fd_device.grainbin.owfs_interface.requests.get",
        return_value=mocker.Mock(status_code=400),
        autospec=True,
    )

    data = fetch_and_parse_page("test_page")

    assert data is None


def test_fetch_and_parse_page_no_text(mocker):
    """Test the fetch_and_parse_page function if improper text is given."""

    mocker.patch(
        "fd_device.grainbin.owfs_interface.requests.get",
        return_value=mocker.Mock(status_code=200, text="Test text no table"),
        autospec=True,
    )

    data = fetch_and_parse_page("test_page")

    assert isinstance(data, list)
    assert len(data) == 0


def test_get_all_busses(mocker):
    """Test the get_all_busses function."""

    with open(f"{CONFIG.TEST_DIR}/grainbin/test_root_owfs_page.txt") as f:
        text_as_list = f.readlines()
        test_text = "/n".join(text_as_list)

    mocker.patch(
        "fd_device.grainbin.owfs_interface.requests.get",
        return_value=mocker.Mock(status_code=200, text=test_text),
        autospec=True,
    )

    all_busses = get_all_busses()

    assert isinstance(all_busses, list)
    assert len(all_busses) == 2


def test_get_all_busses_including_all(mocker):
    """Test the get_all_busses function including fetching the all bus."""

    with open(f"{CONFIG.TEST_DIR}/grainbin/test_root_owfs_page.txt") as f:
        text_as_list = f.readlines()
        test_text = "/n".join(text_as_list)

    mocker.patch(
        "fd_device.grainbin.owfs_interface.requests.get",
        return_value=mocker.Mock(status_code=200, text=test_text),
        autospec=True,
    )

    all_busses = get_all_busses(ignore_all_bus=False)

    assert isinstance(all_busses, list)
    assert len(all_busses) == 3


def test_get_all_sensors_of_bus(mocker):
    """Test the get_all_busses function including fetching the all bus."""

    with open(f"{CONFIG.TEST_DIR}/grainbin/test_bus_1_owfs_page.txt") as f:
        text_as_list = f.readlines()
        test_text = "/n".join(text_as_list)

    mocker.patch(
        "fd_device.grainbin.owfs_interface.requests.get",
        return_value=mocker.Mock(status_code=200, text=test_text),
        autospec=True,
    )

    all_sensors = get_all_sensors_of_bus(bus_name="test bus")

    assert isinstance(all_sensors, list)
    assert len(all_sensors) == 3


def test_read_sensor_of_bus(mocker):
    """Test the read_sensor_of_bus function."""

    with open(f"{CONFIG.TEST_DIR}/grainbin/test_sensor_1_1_owfs_page.txt") as f:
        text_as_list = f.readlines()
        test_text = "/n".join(text_as_list)

    mocker.patch(
        "fd_device.grainbin.owfs_interface.requests.get",
        return_value=mocker.Mock(status_code=200, text=test_text),
        autospec=True,
    )

    sensor_info = read_sensor_of_bus(bus_name="test bus", sensor="test sensor")

    assert isinstance(sensor_info, dict)
    assert "temperature" in sensor_info
    assert "temphigh" in sensor_info
    assert "templow" in sensor_info
