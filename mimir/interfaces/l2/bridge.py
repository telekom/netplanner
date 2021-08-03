from dataclasses import dataclass, field
from typing import List, Optional
from ..base import Base, InterfaceName


@dataclass
class BridgeParameters(Base):
    ageing_time: Optional[int]
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
    vrf: InterfaceName = field(default=InterfaceName('default'))
    interfaces: List[InterfaceName] = field(default_factory=list)

