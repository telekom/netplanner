from dataclasses import dataclass, field
from typing import List, Optional, Set

from netplanner.interfaces.base import Base
from netplanner.interfaces.l3.nameserver import NameServers
from netplanner.interfaces.l3.route import Route
from netplanner.interfaces.l3.routing_policy import RoutingPolicy
from netplanner.interfaces.typing import (
    MTU,
    InterfaceName,
    LinkLocalAdressing,
    PositiveInt,
    BondMode,
)


@dataclass
class BondParameters(Base):
    mode: BondMode
    primary: Optional[InterfaceName]
    mii_monitor_interval: PositiveInt = PositiveInt(100)


@dataclass
class Bond(Base):
    parameters: BondParameters
    vrf: Optional[InterfaceName]
    nameservers: Optional[NameServers]
    mtu: Optional[MTU]
    link_local: Optional[Set[LinkLocalAdressing]]
    interfaces: List[InterfaceName] = field(default_factory=list)
    addresses: List[str] = field(default_factory=list)
    routes: List[Route] = field(default_factory=list)
    routing_policy: List[RoutingPolicy] = field(default_factory=list)

    def __post_init__(self):
        if self.link_local is None:
            self.link_local = set()
            self.link_local.add(LinkLocalAdressing("ipv6"))
