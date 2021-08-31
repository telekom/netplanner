from dataclasses import dataclass, field
from typing import List, Optional, Set

from mimir.interfaces.base import Base
from mimir.interfaces.l3.nameserver import NameServers
from mimir.interfaces.l3.route import Route
from mimir.interfaces.l3.routing_policy import RoutingPolicy
from mimir.interfaces.match_object import MatchObject
from mimir.interfaces.typing import (
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
    mtu: Optional[MTU]
    virtual_function_count: Optional[VirtualFunctionCount]
    link_local: Optional[Set[LinkLocalAdressing]]
    vrf: InterfaceName = InterfaceName("default")
    addresses: IPInterfaceAddresses = field(default_factory=list)
    routes: List[Route] = field(default_factory=list)
    routing_policy: List[RoutingPolicy] = field(default_factory=list)
    emit_lldp: bool = False
    wakeonlan: bool = False

    def __post_init__(self):
        if self.link_local is None:
            self.link_local = set()
            self.link_local.add(LinkLocalAdressing("ipv6"))
