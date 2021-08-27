from dataclasses import dataclass, field
from typing import List, Optional, Set

from mimir.interfaces.l3.nameserver import NameServers
from mimir.interfaces.l3.route import Route
from mimir.interfaces.l3.routing_policy import RoutingPolicy
from mimir.interfaces.typing import IPInterfaceAddresses

from ..base import MTU, Base, InterfaceName, LinkLocalAdressing, MacAddress


@dataclass
class VLAN(Base):
    id: int
    link: InterfaceName
    mtu: Optional[MTU]
    macaddress: Optional[MacAddress]
    nameservers: Optional[NameServers]
    addresses: IPInterfaceAddresses = field(default_factory=list)
    vrf: InterfaceName = InterfaceName("default")
    routes: List[Route] = field(default_factory=list)
    routing_policy: List[RoutingPolicy] = field(default_factory=list)
    link_local: Optional[Set[LinkLocalAdressing]] = field(default_factory=set)

    def __post_init__(self):
        self.link_local.add(LinkLocalAdressing("ipv6"))
        if self.id and not (2 <= self.id <= 4095):
            raise ValueError(f"VLAN Id={self.id} not in 2 - 4095")
