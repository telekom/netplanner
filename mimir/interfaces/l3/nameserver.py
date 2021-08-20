from dataclasses import dataclass, field
from typing import List, Union
from ..base import Base
from ipaddress import IPv4Address, IPv4Network, IPv6Address, IPv6Network


@dataclass
class NameServers(Base):
    search: List[str] = field(default_factory=list)
    addresses: List[Union[IPv4Network, IPv6Network]] = field(default_factory=list)
