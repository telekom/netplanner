from dataclasses import dataclass, field
from mimir.interfaces.typing import IPInterfaceAddresses
from mimir.interfaces.l3.routing_policy import RoutingPolicy
from mimir.interfaces.l3.route import Route
from typing import List, Optional
from mimir.interfaces.l3.nameserver import NameServers
from ..base import MTU, Base, InterfaceName, MacAddress, MatchObject, VirtualFunctionCount


@dataclass
class Ethernet(Base):
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
