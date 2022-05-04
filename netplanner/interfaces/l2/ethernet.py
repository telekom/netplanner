from dataclasses import dataclass, field
from ipaddress import IPv4Address, IPv6Address
from typing import List, Optional, Set

from ..base import Base
from ..l3.nameserver import NameServers
from ..l3.route import Route
from ..l3.routing_policy import RoutingPolicy
from ..match_object import MatchObject
from ..typing import (
    MTU,
    InterfaceName,
    IPInterfaceAddresses,
    LinkLocalAdressing,
    MacAddress,
    VirtualFunctionCount,
)


@dataclass
class Ethernet(Base):
    macaddress: Optional[MacAddress]
    optional: Optional[bool]
    nameservers: Optional[NameServers]
    match: Optional[MatchObject]
    link: Optional[InterfaceName]
    vrf: Optional[InterfaceName]
    mtu: Optional[MTU]
    virtual_function_count: Optional[VirtualFunctionCount]
    link_local: Optional[Set[LinkLocalAdressing]]
    accept_ra: Optional[bool]
    gateway4: Optional[IPv4Address]
    gateway6: Optional[IPv6Address]
    set_name: Optional[InterfaceName]
    addresses: IPInterfaceAddresses = field(default_factory=list)
    routes: List[Route] = field(default_factory=list)
    routing_policy: List[RoutingPolicy] = field(default_factory=list)
    emit_lldp: bool = False
    wakeonlan: bool = False

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
