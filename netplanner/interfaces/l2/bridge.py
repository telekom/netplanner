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
    VLANId,
    VLANType,
)


@dataclass
class BridgeParameters(Base):
    ageing_time: Optional[int]
    vlan_protocol: Optional[VLANType]
    vlan_filtering: Optional[bool]
    default_vlan_port_id: Optional[VLANId]
    priority: Optional[int]
    port_priority: Optional[int]
    forward_delay: Optional[int]
    hello_time: Optional[int]
    max_age: Optional[int]
    path_cost: Optional[int]
    stp: bool = field(default=True)

    def __post_init__(self):
        if self.priority is not None and (self.priority < 0 or self.priority > 65535):
            raise ValueError(
                f"BridgeParameters Priority {self.priority} not in 0 - 65535"
            )
        if self.port_priority is not None and (
            self.port_priority < 0 or self.port_priority > 63
        ):
            raise ValueError(
                f"BridgeParameters Port Priority {self.port_priority} not in 0 - 63"
            )


@dataclass
class Bridge(Base):
    parameters: BridgeParameters
    nameservers: Optional[NameServers]
    vrf: Optional[InterfaceName]
    mtu: Optional[MTU]
    macaddress: Optional[MacAddress]
    link_local: Optional[Set[LinkLocalAdressing]]
    interfaces: List[InterfaceName] = field(default_factory=list)
    addresses: IPInterfaceAddresses = field(default_factory=list)
    routes: List[Route] = field(default_factory=list)
    routing_policy: List[RoutingPolicy] = field(default_factory=list)

    def __post_init__(self):
        if self.link_local is None:
            self.link_local = set()
            self.link_local.add(LinkLocalAdressing("ipv6"))
