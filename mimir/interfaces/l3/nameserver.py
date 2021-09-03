from dataclasses import dataclass, field
from typing import List

from fqdn import FQDN
from mimir.interfaces.base import Base
from mimir.interfaces.typing import IPAddress


@dataclass
class NameServers(Base):
    search: List[FQDN] = field(default_factory=list)
    addresses: List[IPAddress] = field(default_factory=list)
