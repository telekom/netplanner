from dataclasses import dataclass
from mimir.interfaces.l3.nameserver import NameServers
from typing import Optional

from ..base import Base, InterfaceName, MacAddress


@dataclass
class VLAN(Base):
    id: int
    link: InterfaceName
    mtu: Optional[int]
    macaddress: Optional[MacAddress]
    nameservers: Optional[NameServers]
    dhcp4: bool = False
    dhcp6: bool = False
    def __post_init__(self):
        if self.id not in range(4096):
            raise ValueError(f"VLAN Id={self.id} not in 0 - 4095")
        if self.mtu and self.mtu not in range(256,9001):
            raise ValueError(f"VLAN MTUBytes={self.mtu} not in 256 - 9000")