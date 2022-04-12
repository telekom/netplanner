from dataclasses import dataclass
from enum import Enum
from typing import Optional

from netplanner.interfaces.base import MTU, Base, PositiveInt
from netplanner.interfaces.typing import IPAddress, IPNetwork, TableShortInt
from netplanner.interfaces.typing import RouteScope, RouteType


@dataclass
class Route(Base):
    _from: Optional[IPNetwork]
    to: Optional[IPNetwork]
    via: Optional[IPAddress]
    on_link: Optional[bool]
    table: Optional[TableShortInt]
    metric: Optional[int]
    scope: Optional[RouteScope]
    type: Optional[RouteType]
    mtu: Optional[MTU]
    congestion_window: Optional[PositiveInt]
    advertised_receive_window: Optional[PositiveInt]

    def __post_init__(self):
        if not self.on_link and self.via is None:
            raise ValueError(
                f"Route OnLink={self.on_link} and Gateway={self.via}"
            )
