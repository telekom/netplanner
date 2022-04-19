from dataclasses import dataclass, field
from typing import List, Optional, Set

from netplanner.interfaces.base import Base
from netplanner.interfaces.l3.route import Route
from netplanner.interfaces.l3.routing_policy import RoutingPolicy
from netplanner.interfaces.typing import (
    MTU,
    InterfaceName,
    IPInterfaceAddresses,
    MacAddress,
    LinkLocalAdressing,
)


@dataclass
class Veth(Base):
    link: InterfaceName
    optional: Optional[bool]
    macaddress: Optional[MacAddress]
    mtu: Optional[MTU]
    link_local: Optional[Set[LinkLocalAdressing]]
    vrf: Optional[InterfaceName]
    addresses: IPInterfaceAddresses = field(default_factory=list)
    routes: List[Route] = field(default_factory=list)
    routing_policy: List[RoutingPolicy] = field(default_factory=list)

    def __post_init__(self):
        if self.link_local is None:
            self.link_local = set()
            self.link_local.add(LinkLocalAdressing("ipv6"))
