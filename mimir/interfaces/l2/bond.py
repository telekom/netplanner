from dataclasses import dataclass, field
from enum import Enum
from mimir.interfaces.l3.nameserver import NameServers
from mimir.interfaces.l3.route import Route
from mimir.interfaces.l3.routing_policy import RoutingPolicy
from typing import List, Optional, Set
from mimir.interfaces.base import (
    MTU,
    Base,
    InterfaceName,
    LinkLocalAdressing,
    PositiveInt,
)


class BondMode(Enum):
    ACTIVE_BACKUP = "active-backup"
    BALANCE_ROUND_ROBIN = "balance-rr"
    BALANCE_ROUND_ROBIN_EXCLUSIVE = "balance_xor"
    BALANCE_TLB = "balance-tlb"
    BALANCE_ALB = "balance-alb"
    BROADCAST = "broadcast"
    LACP = "802.3ad"


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
        self.link_local.add(LinkLocalAdressing("ipv6"))
