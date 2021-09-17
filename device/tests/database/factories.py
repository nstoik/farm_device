"""Database factories to help in tests."""
# pylint: disable=too-few-public-methods,no-self-argument,unused-argument
from factory import Sequence
from factory.alchemy import SQLAlchemyModelFactory
from factory.declarations import SelfAttribute, SubFactory

from fd_device.database.base import get_session
from fd_device.database.device import Device, Grainbin


class BaseFactory(SQLAlchemyModelFactory):
    """Base factory."""

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override the _create classmethod.

        Does not actually change from the default, but
        for some reason it needs to be specified otherwise
        SubFactory elements do not get the primary key created
        correctly.
        """
        obj = model_class(*args, **kwargs)
        obj.save()
        return obj

    class Meta:
        """Factory configuration."""

        abstract = True
        sqlalchemy_session = get_session()


class DeviceFactory(BaseFactory):
    """Device Factory."""

    device_id = Sequence(lambda n: f"Test Device{n}")

    class Meta:
        """Factory configuration."""

        model = Device


class GrainbinFactory(BaseFactory):
    """Grainbin factory."""

    device = SubFactory(DeviceFactory)
    device_id = SelfAttribute("device.id")
    name = Sequence(lambda n: f"Test Grainbin{n}")
    bus_number = Sequence(int)

    class Meta:
        """Factory Configuration."""

        model = Grainbin
        exclude = ("device",)
