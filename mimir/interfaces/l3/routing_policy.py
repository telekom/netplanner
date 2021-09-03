from dataclasses import dataclass
from typing import Optional

from mimir.interfaces.base import Base, PositiveInt
from mimir.interfaces.typing import IPNetwork


@dataclass
class RoutingPolicy(Base):
    _from: IPNetwork
    to: IPNetwork
    table: Optional[PositiveInt]
    priority: Optional[PositiveInt]
    mark: Optional[PositiveInt]
    type_of_service: Optional[PositiveInt]
