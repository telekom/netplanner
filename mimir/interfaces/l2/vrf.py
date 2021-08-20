from dataclasses import dataclass, field
from ipaddress import IPv4Network, IPv6Network
from mimir.interfaces.l3.routing_policy import RoutingPolicy
from typing import List, Optional, Union

from ..base import Base
from ..l3.nameserver import NameServers
from ..l3.route import Route


@dataclass
class VRF(Base):
    mtu: Optional[int]
    table: int = field(default=254)
    addresses: List[str] = field(default_factory=list)
    routes: List[Route] = field(default_factory=list)
    routing_policy: List[RoutingPolicy] = field(default_factory=list)

    def __init__(self) -> None:
        if self.mtu and not (256 <= self.mtu <= 9166):
            raise ValueError(f"VRF MTUBytes={self.mtu} not in 256 - 9166")