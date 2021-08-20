from dataclasses import dataclass
from ipaddress import IPv4Network, IPv6Network
from typing import Optional, Union

from ..base import Base


@dataclass
class RoutingPolicy(Base):
    _from: str
    to: str
    table: Optional[int]
    priority: Optional[int]
    mark: Optional[int]
    type_of_service: Optional[int]
