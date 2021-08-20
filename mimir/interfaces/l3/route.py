from dataclasses import dataclass
from ipaddress import IPv4Address, IPv4Network, IPv6Address, IPv6Network
from typing import Optional, Union
from ..base import Base
from enum import Enum

class RouteType(Enum):
    UNREACHABLE = "unreachable"
    BLACKHOLE = "blackhole"
    PROHIBIT = "prohibit"
    UNICAST = "unicast"

class RouteScope(Enum):
    GLOBAL = "global"
    LINK = "link"
    HOST = "host"

@dataclass
class Route(Base):
    _from: str
    to: str
    via: str
    on_link: Optional[bool]
    metric: Optional[int]
    scope: Optional[RouteScope]
    type: Optional[RouteType]
    mtu: Optional[int]
    congestion_window: Optional[int] # positive integer
    advertised_receive_window: Optional[int] # positive integer
