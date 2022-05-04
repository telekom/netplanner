from dataclasses import dataclass
from typing import Optional

from ..base import Base, PositiveInt
from ..typing import IPNetwork, TableShortInt, UnsignedShortInt


@dataclass
class RoutingPolicy(Base):
    _from: Optional[IPNetwork]
    to: Optional[IPNetwork]
    table: Optional[TableShortInt]
    priority: Optional[PositiveInt]
    mark: Optional[PositiveInt]
    type_of_service: Optional[UnsignedShortInt]

    def __post_init__(self):
        if not self._from and not self.to and not self.mark:
            raise ValueError("Either from or to must")
