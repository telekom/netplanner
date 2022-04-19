from dataclasses import dataclass, field
from typing import List

from netplanner.interfaces.base import Base, FQDN
from netplanner.interfaces.typing import IPAddress


@dataclass
class NameServers(Base):
    search: List[FQDN] = field(default_factory=list)
    addresses: List[IPAddress] = field(default_factory=list)
