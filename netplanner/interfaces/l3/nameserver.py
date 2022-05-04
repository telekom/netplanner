from dataclasses import dataclass, field
from typing import List

from ..base import FQDN, Base
from ..typing import IPAddress


@dataclass
class NameServers(Base):
    search: List[FQDN] = field(default_factory=list)
    addresses: List[IPAddress] = field(default_factory=list)
