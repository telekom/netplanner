from dataclasses import dataclass
from ipaddress import IPv4Address, IPv4Network, IPv6Address, IPv6Network
from typing import Optional, Union
from ..base import Base

@dataclass
class Route(Base):
    pass
    to: Union[IPv6Network, IPv4Network]
    via: Union[IPv4Address, IPv6Address]
    on_link: Optional[bool]
    metric: Optional[int]