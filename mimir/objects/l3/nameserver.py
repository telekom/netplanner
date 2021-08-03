from dataclasses import dataclass, field
from typing import List, Union
from ..base import Base
from ipaddress import IPv4Address, IPv6Address


@dataclass
class NameServers(Base):
    search: List[str] = field(default_factory=list)
    addresses: List[Union[IPv4Address, IPv6Address]] = field(default_factory=list)
