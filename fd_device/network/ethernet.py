"""Control the ethernet connections of the device."""
import logging

import netifaces
from netifaces import AF_INET

from fd_device.database.base import get_session
from fd_device.database.system import Interface

logger = logging.getLogger("fm.network.ethernet")


def ethernet_connected():
    """Check if 'eth0' has an IP address. Returns True or False."""

    try:
        netifaces.ifaddresses("eth0")[AF_INET][0]
    except KeyError:
        return False

    return True


def get_interfaces(only_wlan=False, only_eth=False):
    """Return the interfaces the device has."""

    logger.debug("getting all interfaces")
    interfaces = netifaces.interfaces()

    if "lo" in interfaces:
        interfaces.remove("lo")

    if only_wlan:
        for x in interfaces:
            if not x.startswith("wlan"):
                interfaces.remove(x)

    if only_eth:
        for x in interfaces:
            if not x.startswith("eth"):
                interfaces.remove(x)

    return interfaces


def get_external_interface():
    """Return the external interface.

    This is the interface that is used to send traffic out for any AP.
    First check if eth0 is present. Then check if there is a wlan
    interface that has a state of 'dhcp'
    """

    session = get_session()

    if ethernet_connected():
        ethernet = session.query(Interface).filter_by(interface="eth0").first()
        ethernet.is_external = True
        session.commit()
        session.close()
        return "eth0"

    # now check if it is either wlan0 or wlan1
    interfaces = session.query(Interface).filter_by(state="dhcp").all()

    for interface in interfaces:
        if interface.interface != "eth0":
            interface.is_external = True
            session.commit()
            session.close()
            return interface.interface

    session.close()
    return "None"
