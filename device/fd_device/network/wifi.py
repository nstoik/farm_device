"""Control the wifi connections of the device."""
import logging
import subprocess
from typing import List, Optional, TypedDict

import netifaces
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.session import object_session

from fd_device.database.database import get_session
from fd_device.database.system import Interface, Wifi
from fd_device.network.ethernet import get_external_interface, get_interfaces
from fd_device.network.network_files import (
    dhcpcd_file,
    dnsmasq_file,
    hostapd_file,
    interface_file,
    iptables_file,
    wpa_supplicant_file,
)
from fd_device.settings import get_config

logger = logging.getLogger("fd.network.wifi")


def refresh_interfaces():
    """Refresh all interfaces. Update with current information."""

    session = get_session()
    ap_present = False

    interfaces = get_interfaces()

    # update all interfaces.active to be False by default
    session.query(Interface).update({Interface.is_active: False})

    for my_interface in interfaces:
        try:
            interface = session.query(Interface).filter_by(interface=my_interface).one()

            interface.is_active = True
            # see if there is an interface that is configured for an ap
            if interface.state == "ap":
                ap_present = True

        # must be a new interface so lets add it
        except NoResultFound:
            new_interface = Interface(my_interface)
            new_interface.is_active = True
            new_interface.is_for_fm = False
            new_interface.state = "dhcp"
            session.add(new_interface)

    session.commit()
    session.close()

    if ap_present:
        set_ap_mode()
    else:
        set_wpa_mode()


def scan_wifi(interface=None) -> List:
    """Scan the interface for the available wifi networks.

    Args:
        interface (str, optional): the interface to search on. Defaults to None.
        if no interface is given, try an interface from the database that is 'dhcp'

    Returns:
        List: A list of strings that are the found networks
    """

    # if no interface is given, try find an interface in the database
    # that has the state set to 'dhcp' and is not 'eth'
    if interface is None:
        session = get_session()

        interfaces = session.query(Interface).all()
        for x in interfaces:
            if not x.interface.startswith("eth"):
                if x.state == "dhcp":
                    interface = x.interface

        session.close()

    # exit if still no interface
    if interface is None:
        logger.warning("No interface available to scan wifi networks")
        return []

    # scan the interface for networks
    command = ["sudo", "iwlist", interface, "scan"]
    output = subprocess.check_output(command, universal_newlines=True)
    index = output.find('ESSID:"')
    ssid = []
    while index > 0:
        stop = output.find('"\n', index)

        ssid.append(output[index + 7 : stop])

        output = output[stop + 2 :]

        index = output.find('ESSID:"')

    return ssid


def add_wifi_network(
    wifi_name: str, wifi_password: str, interface: Interface | None = None
) -> Optional[Wifi]:
    """Add a wifi entry to the database of stored WiFi networks.

    Args:
        wifi_name (str): The SSID of the WiFi network.
        wifi_password (str): The password of the WiFi network.
        interface (Interface, optional): The Interface to assign the WiFi to.
        If None, the first 'wlan' interface set to DHCP is used. Defaults to None.

    Returns:
        Optional[Wifi]: The WiFi instance that was created or None if no Interface is found.
    """

    # if no interface is passed in, create a session and look for a valid interface
    if interface is None:
        session = get_session()
        interfaces = session.query(Interface).all()
        for x in interfaces:
            # find first available wlan interface that is not dhcp
            if x.interface != "eth0" and x.state == "dhcp":
                interface = x
                break
    # if an interface is passed in, get the session from the interface.
    else:
        retrieved_session = object_session(interface)
        if retrieved_session is None:
            logger.error("No session available from the supplied interface")
            session = get_session()
        else:
            session = retrieved_session

    if interface is None:
        logger.error("No interface available to add new wifi network")
        return None

    # have an interface. now create a Wifi entry
    new_wifi = Wifi()
    new_wifi.name = wifi_name
    new_wifi.password = wifi_password
    new_wifi.mode = "dhcp"
    new_wifi.interface = interface

    new_wifi.save(session)

    return new_wifi


def delete_wifi_network(wifi_id: str) -> bool:
    """Delete a WiFi network.

    Args:
        wifi_id (str): The ID of the WiFi netowrk to delete

    Returns:
        bool: True if an entry was deleted. False if nothing was deleted.
    """

    session = get_session()

    deleted_count = session.query(Wifi).filter_by(id=wifi_id).delete()
    session.commit()
    session.close()

    return bool(deleted_count > 0)


class WifiInfo(TypedDict):
    """The information that is returned from the wifi_info function."""

    interface: Interface
    clients: int
    ssid: str
    password: str
    state: str
    state_boolean: bool
    address: str


def wifi_info() -> List[WifiInfo]:
    """Get a list of WiFi details for all wlan interfaces.

    Returns:
        List: For each interface, a dictionary of details is added to the list
                Keys of the dictionary are:
                    interface: the interface
                    if ap:
                        clients: the number of clients currently connected
                        ssid: the ssid of the ap
                        password: the password of the ap
                    if dhcp:
                        state: either the SSID currently connected to or False
                        state_boolean: boolean value for state. True or False
                        if state:
                            address: the IPV4 address
                        ssid: the ssid of the dhcp interface
                        password: the password of the dhcp interface
    """
    logger.debug("getting wifi information")

    wlan_interfaces = get_interfaces(keep_eth=False)

    wifi: List[WifiInfo] = []

    session = get_session()

    for w_interface in wlan_interfaces:
        try:
            interface = session.query(Interface).filter_by(interface=w_interface).one()
            if interface.state == "ap":
                wifi_clients = wifi_ap_clients(interface.interface)
                wifi_ssid = interface.credentials[0].name
                wifi_password = interface.credentials[0].password
                wifi_state = "ap"
                wifi_state_boolean = True
                wifi_address = ""
            else:
                wifi_clients = 0
                wifi_ssid = ""
                wifi_password = ""
                wifi_state = wifi_dhcp_info(interface.interface)
                wifi_address = ""
                if wifi_state == "Not connected":
                    wifi_state_boolean = False
                else:
                    wifi_state_boolean = True
                    if w_interface in netifaces.interfaces():
                        address = netifaces.ifaddresses(w_interface)
                        wifi_address = address[netifaces.AF_INET][0]["addr"]

                if interface.credentials:
                    wifi_ssid = interface.credentials[0].name
                    wifi_password = interface.credentials[0].password
            wifi.append(
                WifiInfo(
                    interface=interface,
                    clients=wifi_clients,
                    ssid=wifi_ssid,
                    password=wifi_password,
                    state=wifi_state,
                    state_boolean=wifi_state_boolean,
                    address=wifi_address,
                )
            )

        except NoResultFound:
            pass

    session.close()
    return wifi


def wifi_ap_clients(interface: str) -> int:
    """Get the list of ap clients an interface has.

    Args:
        interface (str): The interface to get the details for.

    Returns:
        int: The number of clients connected to the interface.
    """

    logger.debug("getting wifi clients")
    command = ["iw", "dev", interface, "station", "dump"]
    client_info = subprocess.check_output(command, universal_newlines=True)

    client_count = client_info.count("Station")

    return client_count


def wifi_dhcp_info(interface: str) -> str:
    """Return the SSID that is connected for a given interface.

    Args:
        interface (str): The interface to check. eg. 'wlan0'

    Returns:
        str: The SSID for the interface, or 'Not connected' if the interface is not connected.
    """

    command = ["iw", interface, "link"]
    output = subprocess.check_output(command, universal_newlines=True)

    if output.startswith("Not connected."):
        return "Not connected"

    start_index = output.find("SSID: ")
    end_index = output.find("\n", start_index)
    ssid = output[start_index + 6 : end_index]

    return ssid


def set_interfaces(interfaces: List):
    """Set interface information into database and configure hardware accordingly.

    Args:
        interfaces (List): A list of dictionaries with the required information.
    """

    session = get_session()
    wifi_ap_present = False

    for interface in interfaces:
        try:
            db_result = (
                session.query(Interface).filter_by(interface=interface["name"]).one()
            )
        except NoResultFound:
            db_result = Interface(interface["name"])
            session.add(db_result)
        db_result.is_active = True
        db_result.is_for_fm = interface["is_for_fm"]
        db_result.state = interface["state"]
        if interface["state"] == "ap":
            wifi_ap_present = True
        if "creds" in interface:
            add_wifi_network(
                wifi_name=interface["creds"]["ssid"],
                wifi_password=interface["creds"]["password"],
                interface=db_result,
            )
    session.commit()

    if wifi_ap_present:
        set_ap_mode()
    else:
        set_wpa_mode()


def set_ap_mode():
    """Perform the setup and intialization work for interfaces with an ap present."""

    logger.debug("setting wifi into ap mode")
    session = get_session()

    # get the wlan0 and wlan1 dhcp states
    try:
        ap_interface = session.query(Interface).filter_by(state="ap").first()
        ap_ssid = ap_interface.credentials[0].name
        ap_password = ap_interface.credentials[0].password

    except NoResultFound:
        # error. abort
        logger.warning("No interface with state set to 'ap'. Aborting")
        return

    # get info for interface file
    if ap_interface.interface == "wlan0":
        wlan0_dhcp = False
        wlan1_dhcp = True

    else:
        wlan0_dhcp = True
        wlan1_dhcp = False

    # get the info for the wpa_supplicant file
    wifi_defs = session.query(Wifi).filter(Wifi.mode != "ap").all()
    networks = []
    for wifi in wifi_defs:
        new_network = {}
        new_network["ssid"] = wifi.name
        new_network["password"] = wifi.password
        networks.append(new_network)

    # get the information for the iptables_file
    internal_interface = ap_interface.interface
    external_interface = get_external_interface()

    iptables_file(external_interface, internal_interface)
    interface_file(wlan0_dhcp=wlan0_dhcp, wlan1_dhcp=wlan1_dhcp)
    wpa_supplicant_file(networks)
    dhcpcd_file(interface=ap_interface.interface)
    dnsmasq_file(interface=ap_interface.interface)
    hostapd_file(ap_interface.interface, ap_ssid, ap_password)

    config = get_config()

    path = config.APP_DIR + "/network/ap_script.sh"

    command = ["sudo", "sh", path, ap_interface.interface]
    subprocess.check_call(command)

    session.close()


def set_wpa_mode():
    """Perform the setup and intialization work for interfaces with no ap present."""

    logger.debug("setting all wlan into wpa mode")
    session = get_session()

    # get the info for the wpa_supplicant file
    wifi_defs = session.query(Wifi).filter(Wifi.mode != "ap").all()
    networks = []
    for wifi in wifi_defs:
        new_network = {}
        new_network["ssid"] = wifi.name
        new_network["password"] = wifi.password
        networks.append(new_network)

    iptables_file(None, None, flush_only=True)
    interface_file()
    wpa_supplicant_file(networks)
    dhcpcd_file()

    config = get_config()
    path = config.APP_DIR + "/network/wpa_script.sh"

    command = ["sudo", "sh", path]
    subprocess.check_call(command)
    session.close()
