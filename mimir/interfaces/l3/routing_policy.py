from dataclasses import dataclass
from ipaddress import IPv4Network, IPv6Network
from mimir.interfaces.typing import IPNetwork
from typing import Optional

from ..base import Base, PositiveInt


@dataclass
class RoutingPolicy(Base):
    _from: IPNetwork
    to: IPNetwork
    table: Optional[PositiveInt]
    priority: Optional[PositiveInt]
    mark: Optional[PositiveInt]
    type_of_service: Optional[PositiveInt]
