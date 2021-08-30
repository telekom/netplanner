from dataclasses import dataclass, field
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
    VLANType,
    VLANId,
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
    addresses: IPInterfaceAddresses = field(default_factory=list)
    vrf: InterfaceName = InterfaceName("default")
    routes: List[Route] = field(default_factory=list)
    routing_policy: List[RoutingPolicy] = field(default_factory=list)
    link_local: Optional[Set[LinkLocalAdressing]] = field(default_factory=set)

    def __post_init__(self):
        self.link_local.add(LinkLocalAdressing("ipv6"))
