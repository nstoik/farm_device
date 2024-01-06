"""Create a device update object."""
import datetime

from sqlalchemy import select

from fd_device.database.database import get_session
from fd_device.database.device import Device
from fd_device.device.temperature import temperature


def get_device_info(session=None) -> dict:
    """Return a device information dictionary."""

    close_session = False
    if not session:
        close_session = True
        session = get_session()

    device = session.scalars(select(Device).limit(1)).first()
    if device is None:
        # this is an error, there should always be a device
        return {}

    device.interior_temp = temperature(device.interior_sensor)
    device.exterior_temp = temperature(device.exterior_sensor)
    session.commit()

    info: dict = {}
    info["created_at"] = datetime.datetime.now()
    info["id"] = device.device_id

    device_info = {}
    device_info["device_id"] = device.device_id
    device_info["hardware_version"] = device.hardware_version
    device_info["software_version"] = device.software_version
    device_info["interior_temp"] = device.interior_temp
    device_info["exterior_temp"] = device.exterior_temp
    device_info["grainbin_count"] = device.grainbin_count
    device_info["last_updated"] = device.last_updated

    info["data"] = device_info

    if close_session:
        session.close()

    return info
