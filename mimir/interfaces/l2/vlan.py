from dataclasses import dataclass, field
from ipaddress import IPv4Network, IPv6Network
from typing import List, Optional, Union

from mimir.interfaces.l3.nameserver import NameServers
from mimir.interfaces.l3.route import Route
from mimir.interfaces.l3.routing_policy import RoutingPolicy

from ..base import Base, InterfaceName, MacAddress


@dataclass
class VLAN(Base):
    id: int
    link: InterfaceName
    mtu: Optional[int]
    macaddress: Optional[MacAddress]
    nameservers: Optional[NameServers]
    addresses: List[Union[IPv4Network, IPv6Network]] = field(default_factory=list)
    vrf: InterfaceName = InterfaceName("default")
    routes: List[Route] = field(default_factory=list)
    routing_policy: List[RoutingPolicy] = field(default_factory=list)

    def __post_init__(self):
        if self.id and not (0 <= self.id <= 4095):
            raise ValueError(f"VLAN Id={self.id} not in 0 - 4095")
        if self.mtu and not (256 <= self.mtu <= 9166):
            raise ValueError(f"VLAN MTUBytes={self.mtu} not in 256 - 9166")
        print(self.addresses)
