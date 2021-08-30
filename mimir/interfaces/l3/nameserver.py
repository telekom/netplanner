from dataclasses import dataclass, field
from mimir.interfaces.typing import IPAddress
from typing import List
from ..base import Base
from fqdn import FQDN


@dataclass
class NameServers(Base):
    search: List[FQDN] = field(default_factory=list)
    addresses: List[IPAddress] = field(default_factory=list)
