from dataclasses import dataclass, field
from typing import List, Optional, Set

from ..base import Base
from ..l3.nameserver import NameServers
from ..l3.route import Route
from ..l3.routing_policy import RoutingPolicy
from ..typing import (
    MTU,
    IPInterfaceAddresses,
    LinkLocalAdressing,
    MacAddress,
    TableShortInt,
)


@dataclass
class VRF(Base):
    mtu: Optional[MTU]
    nameservers: Optional[NameServers]
    macaddress: Optional[MacAddress]
    table: TableShortInt  # = field(default=254) this is the table for the default vrf
    link_local: Optional[Set[LinkLocalAdressing]]
    addresses: IPInterfaceAddresses = field(default_factory=list)
    routes: List[Route] = field(default_factory=list)
    routing_policy: List[RoutingPolicy] = field(default_factory=list)

    def __post_init__(self):
        if self.link_local is None:
            self.link_local = set()
            self.link_local.add(LinkLocalAdressing("ipv6"))
