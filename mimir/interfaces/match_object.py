from dataclasses import dataclass
from typing import Optional

from .base import Base
from .typing import InterfaceName, MacAddress


@dataclass
class MatchObject(Base):
    name: Optional[InterfaceName]
    macaddress: Optional[MacAddress]
    driver: Optional[str]
    pciaddress: Optional[str]
