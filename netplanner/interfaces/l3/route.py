from dataclasses import dataclass
from enum import Enum
from typing import Optional

from netplanner.interfaces.base import MTU, Base, PositiveInt
from netplanner.interfaces.typing import IPAddress, IPNetwork, TableShortInt
from netplanner.interfaces.typing import RouteScope, RouteType


@dataclass
class Route(Base):
    _from: Optional[IPNetwork]
    to: IPNetwork
    via: IPAddress
    on_link: Optional[bool]
    table: Optional[TableShortInt]
    metric: Optional[int]
    scope: Optional[RouteScope]
    type: Optional[RouteType]
    mtu: Optional[MTU]
    congestion_window: Optional[PositiveInt]
    advertised_receive_window: Optional[PositiveInt]
