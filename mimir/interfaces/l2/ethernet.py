from dataclasses import dataclass, field, fields
from ipaddress import IPv4Network, IPv6Network
from mimir.interfaces.l3.routing_policy import RoutingPolicy
from mimir.interfaces.l3.route import Route
from typing import List, Optional, Union
from mimir.interfaces.l3.nameserver import NameServers
from ..base import Base, InterfaceName, MacAddress, MatchObject


@dataclass
class Ethernet(Base):
    macaddress: Optional[MacAddress]
    optional: Optional[bool]
    nameservers: Optional[NameServers]
    match: Optional[MatchObject]
    link: Optional[InterfaceName]
    mtu: Optional[int]
    virtual_function_count: Optional[int]
    dhcp4: bool = False
    dhcp6: bool = False
    vrf: InterfaceName = InterfaceName("default")
    addresses: List[Union[IPv4Network, IPv6Network]] = field(default_factory=list)
    routes: List[Route] = field(default_factory=list)
    routing_policy: List[RoutingPolicy] = field(default_factory=list)


    def __post_init__(self):
        if self.virtual_function_count and self.virtual_function_count not in range(256):
            raise ValueError(f"Ethernet virtual_function_count={self.virtual_function_count} not in 0 - 255")
