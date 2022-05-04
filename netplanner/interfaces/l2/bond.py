from dataclasses import dataclass, field
from ipaddress import IPv4Address, IPv6Address
from typing import List, Optional, Set

from ..base import Base
from ..l3.nameserver import NameServers
from ..l3.route import Route
from ..l3.routing_policy import RoutingPolicy
from ..typing import (
    MTU,
    BondADSelect,
    BondLACPRate,
    BondMode,
    BondTransmitHashPolicy,
    InterfaceName,
    LinkLocalAdressing,
    MacAddress,
    PositiveInt,
)


@dataclass
class BondParameters(Base):
    mode: BondMode
    primary: Optional[InterfaceName]
    transmit_hash_policy: Optional[BondTransmitHashPolicy]
    ad_select: Optional[BondADSelect]
    lacp_rate: BondLACPRate = BondLACPRate.FAST
    mii_monitor_interval: PositiveInt = PositiveInt(100)


@dataclass
class Bond(Base):
    macaddress: Optional[MacAddress]
    parameters: BondParameters
    vrf: Optional[InterfaceName]
    nameservers: Optional[NameServers]
    mtu: Optional[MTU]
    link_local: Optional[Set[LinkLocalAdressing]]
    gateway4: Optional[IPv4Address]
    gateway6: Optional[IPv6Address]
    interfaces: List[InterfaceName] = field(default_factory=list)
    addresses: List[str] = field(default_factory=list)
    routes: List[Route] = field(default_factory=list)
    routing_policy: List[RoutingPolicy] = field(default_factory=list)

    def __post_init__(self):
        if self.link_local is None:
            self.link_local = set()
            self.link_local.add(LinkLocalAdressing("ipv6"))
        if self.gateway4 is not None:
            self.routes.append(
                Route(
                    description="Default gateway set by gateway4",
                    _from=None,
                    to=None,
                    type=None,
                    via=self.gateway4,
                    on_link=None,
                    table=None,
                    metric=None,
                    scope=None,
                    mtu=None,
                    congestion_window=None,
                    advertised_receive_window=None,
                )
            )
        if self.gateway6 is not None:
            self.routes.append(
                Route(
                    description="Default gateway set by gateway6",
                    _from=None,
                    to=None,
                    type=None,
                    via=self.gateway6,
                    on_link=None,
                    table=None,
                    metric=None,
                    scope=None,
                    mtu=None,
                    congestion_window=None,
                    advertised_receive_window=None,
                )
            )
