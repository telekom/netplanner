from dataclasses import dataclass, field
from mimir.interfaces.base import BaseSerializer
from typing import Dict, Optional
from mimir.interfaces.typing import InterfaceName, MacAddress, PositiveInt


@dataclass
class SRIOVMatchObject(BaseSerializer):
    pciaddress: Optional[str]
    macaddress: Optional[MacAddress]


@dataclass
class Interface(BaseSerializer):
    num_vfs: PositiveInt
    match: Optional[SRIOVMatchObject]


@dataclass
class SRIOVConfig(BaseSerializer):
    interfaces: Dict[InterfaceName, Interface] = field(default_factory=dict)
