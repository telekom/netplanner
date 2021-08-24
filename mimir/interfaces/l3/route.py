from dataclasses import dataclass
from ipaddress import IPv4Address, IPv4Network, IPv6Address, IPv6Network
from mimir.interfaces.typing import IPAddress, IPNetwork
from typing import Optional, Union
from ..base import MTU, Base, PositiveInt
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
    _from: IPNetwork
    to: IPNetwork
    via: IPAddress
    on_link: Optional[bool]
    metric: Optional[int]
    scope: Optional[RouteScope]
    type: Optional[RouteType]
    mtu: Optional[MTU]
    congestion_window: Optional[PositiveInt]
    advertised_receive_window: Optional[PositiveInt]
