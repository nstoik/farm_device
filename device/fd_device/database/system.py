"""The system models for the database."""
# pylint: disable=duplicate-code
from datetime import datetime
from typing import List, Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .database import SurrogatePK, reference_col, str20

# pylint: enable=duplicate-code

# https://github.com/pylint-dev/pylint/issues/8138
# can be removed once upstream issue in pylint is fixed
# pylint: disable=not-callable


class SystemSetup(SurrogatePK):
    """The state of the setup of the system."""

    __tablename__ = "system_setup"

    first_setup: Mapped[bool] = mapped_column(default=False)
    first_setup_time: Mapped[datetime] = mapped_column(default=func.now())
    standalone_configuration: Mapped[bool] = mapped_column(default=True)

    def __init__(self):
        """Create the SystemSetup object."""
        return


class Wifi(SurrogatePK):
    """The wifi connections of the device."""

    __tablename__ = "system_wifi"

    name: Mapped[str20] = mapped_column(default="FarmMonitor")
    password: Mapped[str20] = mapped_column(default="raspberry")
    mode: Mapped[str20] = mapped_column(default="wpa")

    interface_id: Mapped[int] = reference_col("system_interface", nullable=True)
    interface: Mapped["Interface"] = relationship(back_populates="credentials")

    def __init__(self):
        """Create the Wifi object."""
        return


class Interface(SurrogatePK):
    """The interface connections of the device."""

    __tablename__ = "system_interface"

    interface: Mapped[str] = mapped_column(String(5), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_for_fm: Mapped[bool] = mapped_column(default=False)
    is_external: Mapped[bool] = mapped_column(default=False)
    state: Mapped[Optional[str20]]

    credentials: Mapped[List["Wifi"]] = relationship(back_populates="interface")

    def __init__(self, interface):
        """Create the interface object."""

        self.interface = interface


class Hardware(SurrogatePK):
    """The hardware representation of the device."""

    __tablename__ = "system_hardware"

    device_name: Mapped[Optional[str20]]
    hardware_version: Mapped[Optional[str20]]

    interior_sensor: Mapped[str20] = mapped_column(nullable=True, default=None)
    exterior_sensor: Mapped[str20] = mapped_column(nullable=True, default=None)

    serial_number: Mapped[Optional[str20]]
    grainbin_reader_count: Mapped[int] = mapped_column(default=0)

    def __init__(self):
        """Create the Hardware object."""
        return


class Software(SurrogatePK):
    """The software representation of the device."""

    __tablename__ = "system_software"

    software_version: Mapped[Optional[str20]]
    software_version_last: Mapped[Optional[str20]]

    def __init__(self):
        """Create the Software object."""
        return
