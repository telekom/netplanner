from dataclasses import dataclass, field
from typing import Union, List
from .base import Base, InterfaceName
from ipaddress import IPv4Network, IPv6Network
from .l3.route import Route
from .l3.nameserver import NameServers


@dataclass
class VLAN(Base):
    id: int
    link: InterfaceName
    nameservers: NameServers
    addresses: List[Union[IPv4Network, IPv6Network]] = field(default_factory=list)
    routes: List[Route] = field(default_factory=list)

    def __post_init__(self):
        if self.id < 0 or self.id > 4095:
            raise ValueError(f"VLAN Id {self.id} not in 0 - 4095")
