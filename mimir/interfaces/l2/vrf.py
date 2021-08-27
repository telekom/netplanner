from dataclasses import dataclass, field
from mimir.interfaces.typing import IPInterfaceAddresses
from mimir.interfaces.l3.routing_policy import RoutingPolicy
from typing import List, Optional, Set

from ..base import MTU, Base, LinkLocalAdressing, PositiveInt
from ..l3.route import Route


@dataclass
class VRF(Base):
    mtu: Optional[MTU]
    table: PositiveInt = field(default=254)
    addresses: IPInterfaceAddresses = field(default_factory=list)
    routes: List[Route] = field(default_factory=list)
    routing_policy: List[RoutingPolicy] = field(default_factory=list)
    link_local: Optional[Set[LinkLocalAdressing]] = field(default_factory=set)

    def __post_init__(self):
        self.link_local.add(LinkLocalAdressing("ipv6"))
