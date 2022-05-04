from dataclasses import dataclass, field
from ipaddress import IPv4Address, IPv6Address
from typing import List, Optional, Set

from ..base import Base
from ..l3.nameserver import NameServers
from ..l3.route import Route
from ..l3.routing_policy import RoutingPolicy
from ..typing import (
    MTU,
    InterfaceName,
    IPInterfaceAddresses,
    LinkLocalAdressing,
    MacAddress,
    VLANId,
    VLANType,
)


@dataclass
class VLANParameters(Base):
    protocol: Optional[VLANType]
    gvrp: Optional[bool]
    mvrp: Optional[bool]
    loose_binding: Optional[bool]
    reorder_header: Optional[bool]


@dataclass
class VLAN(Base):
    id: VLANId
    link: InterfaceName
    mtu: Optional[MTU]
    parameters: Optional[VLANParameters]
    macaddress: Optional[MacAddress]
    nameservers: Optional[NameServers]
    link_local: Optional[Set[LinkLocalAdressing]]
    vrf: Optional[InterfaceName]
    gateway4: Optional[IPv4Address]
    gateway6: Optional[IPv6Address]
    addresses: IPInterfaceAddresses = field(default_factory=list)
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
