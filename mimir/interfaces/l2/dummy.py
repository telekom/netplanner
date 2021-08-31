from dataclasses import dataclass, field
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
class Dummy(Base):
    macaddress: Optional[MacAddress]
    optional: Optional[bool]
    nameservers: Optional[NameServers]
    match: Optional[MatchObject]
    link: Optional[InterfaceName]
    mtu: Optional[MTU]
    virtual_function_count: Optional[VirtualFunctionCount]
    vrf: InterfaceName = InterfaceName("default")
    addresses: IPInterfaceAddresses = field(default_factory=list)
    routes: List[Route] = field(default_factory=list)
    routing_policy: List[RoutingPolicy] = field(default_factory=list)
    emit_lldp: bool = False
    wakeonlan: bool = False
    link_local: Optional[Set[LinkLocalAdressing]] = field(default_factory=set)

    def __post_init__(self):
        self.link_local.add(LinkLocalAdressing("ipv6"))
