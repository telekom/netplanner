from dataclasses import dataclass, field
from typing import List, Optional, Set

from ..base import Base
from ..l3.route import Route
from ..l3.routing_policy import RoutingPolicy
from ..typing import (
    MTU,
    InterfaceName,
    IPInterfaceAddresses,
    LinkLocalAdressing,
    MacAddress,
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
