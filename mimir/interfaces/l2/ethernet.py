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
    vrf: InterfaceName = InterfaceName("default")
    addresses: List[Union[IPv4Network, IPv6Network]] = field(default_factory=list)
    routes: List[Route] = field(default_factory=list)
    routing_policy: List[RoutingPolicy] = field(default_factory=list)


    def __post_init__(self):
        if self.virtual_function_count and not(0 <= self.virtual_function_count <= 255):
            raise ValueError(f"Ethernet virtual_function_count={self.virtual_function_count} not in 0 - 255")
        if self.mtu and not (256 <= self.mtu <= 9166):
            raise ValueError(f"Ethernet MTUBytes={self.mtu} not in 256 - 9166")
