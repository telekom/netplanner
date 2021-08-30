from mimir.interfaces.l3.nameserver import NameServers
from typing import Union, List
from ipaddress import (
    IPv4Address,
    IPv4Interface,
    IPv4Network,
    IPv6Address,
    IPv6Interface,
    IPv6Network,
)

IPInterfaceAddresses = List[Union[IPv4Interface, IPv6Interface]]
IPNetwork = Union[IPv4Network, IPv6Network]
IPAddress = Union[IPv4Address, IPv6Address]
