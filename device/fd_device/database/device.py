"""The device models for the database."""
from datetime import datetime
from typing import List, Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .database import SurrogatePK, reference_col, str7, str20

# https://github.com/pylint-dev/pylint/issues/8138
# can be removed once upstream issue in pylint is fixed
# pylint: disable=not-callable


class Connection(SurrogatePK):
    """Represent the device's connecticon to the server."""

    __tablename__ = "connection"
    address: Mapped[Optional[str20]]
    last_updated: Mapped[Optional[datetime]] = mapped_column(onupdate=func.now())
    first_connected: Mapped[datetime] = mapped_column(default=func.now())
    is_connected: Mapped[bool] = mapped_column(default=False)


class Grainbin(SurrogatePK):
    """Represent a Grainbin that is connected to the device."""

    __tablename__ = "grainbin"
    name: Mapped[str20] = mapped_column(unique=True)
    bus_number: Mapped[int]
    bus_number_string: Mapped[str] = mapped_column(String(10), nullable=True)
    creation_time: Mapped[datetime] = mapped_column(default=func.now())
    last_updated: Mapped[datetime] = mapped_column(
        default=func.now(), onupdate=func.now()
    )
    average_temp: Mapped[str7]

    device_id: Mapped[int] = reference_col("device")

    def __init__(self, name: str, bus_number: int, device_id: int):
        """Create the Grainbin object."""
        self.name = name
        self.bus_number = bus_number
        self.bus_number_string = f"bus.{bus_number}"
        self.device_id = device_id
        self.average_temp = "unknown"

    def __repr__(self):
        """Represent the grainbin in a useful format."""
        return f"<Grainbin name={self.name}"


class Device(SurrogatePK):
    """Represent the Device."""

    __tablename__ = "device"
    device_id: Mapped[str20] = mapped_column(unique=True)
    hardware_version: Mapped[Optional[str20]]
    software_version: Mapped[Optional[str20]]
    creation_time: Mapped[datetime] = mapped_column(default=func.now())
    last_updated: Mapped[datetime] = mapped_column(
        default=func.now(), onupdate=func.now()
    )

    interior_sensor: Mapped[Optional[str20]]
    exterior_sensor: Mapped[Optional[str20]]
    interior_temp: Mapped[Optional[str7]]
    exterior_temp: Mapped[Optional[str7]]

    # grainbin related data
    grainbin_count: Mapped[int] = mapped_column(default=0)
    grainbins: Mapped[List["Grainbin"]] = relationship(backref="device")

    def __init__(self, device_id: str, interior_sensor="null", exterior_sensor="null"):
        """Create the Device object."""
        self.device_id = device_id
        self.interior_sensor = interior_sensor
        self.exterior_sensor = exterior_sensor

    def __repr__(self):
        """Represent the device in a useful format."""
        return f"<Device: device_id={self.device_id}>"
