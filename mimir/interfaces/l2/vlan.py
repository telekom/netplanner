from dataclasses import dataclass, field
from typing import List, Optional, Set

from mimir.interfaces.base import Base
from mimir.interfaces.l3.nameserver import NameServers
from mimir.interfaces.l3.route import Route
from mimir.interfaces.l3.routing_policy import RoutingPolicy
from mimir.interfaces.typing import (
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
    gvrp: Optional[bool] = None
    mvrp: Optional[bool] = None
    loose_binding: Optional[bool] = None
    reorder_header: Optional[bool] = None


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
    addresses: IPInterfaceAddresses = field(default_factory=list)
    routes: List[Route] = field(default_factory=list)
    routing_policy: List[RoutingPolicy] = field(default_factory=list)

    def __post_init__(self):
        if self.link_local is None:
            self.link_local = set()
            self.link_local.add(LinkLocalAdressing("ipv6"))
