from dataclasses import dataclass, field
from typing import List, Optional, Set

from ..base import Base
from ..l3.nameserver import NameServers
from ..l3.route import Route
from ..l3.routing_policy import RoutingPolicy
from ..typing import MTU, InterfaceName, LinkLocalAdressing, PositiveInt, BondMode


@dataclass
class BondParameters(Base):
    mode: BondMode
    primary: Optional[InterfaceName]
    mii_monitor_interval: Optional[PositiveInt]


@dataclass(frozen=True)
class Bond(Base):
    parameters: BondParameters
    vrf: Optional[InterfaceName]
    nameservers: Optional[NameServers]
    mtu: Optional[MTU]
    interfaces: List[InterfaceName] = field(default_factory=list)
    addresses: List[str] = field(default_factory=list)
    routes: List[Route] = field(default_factory=list)
    routing_policy: List[RoutingPolicy] = field(default_factory=list)
    link_local: Optional[Set[LinkLocalAdressing]] = field(default_factory=set)

    def __post_init__(self):
        if self.link_local is None:
            self.link_local.add(LinkLocalAdressing("ipv6"))
