from dataclasses import dataclass, field

import dacite
from mimir.objects.vf import VF
from typing import Dict
from .objects.base import Base, Version, InterfaceName, NetworkRenderer
from enum import Enum
from .objects.ethernet import Ethernet
from .objects.bridge import Bridge
from .objects.vxlan import VXLAN
from .objects.vlan import VLAN


@dataclass
class NetplanConfig(Base):
    version: Version
    renderer: NetworkRenderer
    ethernets: Dict[InterfaceName, Ethernet] = field(default_factory=dict)
    bridges: Dict[InterfaceName, Bridge] = field(default_factory=dict)
    vxlans: Dict[InterfaceName, VXLAN] = field(default_factory=dict)
    vlans: Dict[InterfaceName, VLAN] = field(default_factory=dict)
    vfs: Dict[InterfaceName, VF] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict):
        return super().from_dict(
            data,
            dacite.Config(
                cast=[
                    Enum,
                    InterfaceName
                ]
            ),
        )


if __name__ == "__main__":
    config = NetplanConfig.from_dict(
        {
            "version": 3,
            "renderer": "networkd",
            "bridges": 
                {
                    "br0": {
                        "parameters": {},
                        "interfaces": []
                    }
                }
        }
    )
    print(config)
    assert config.renderer == NetworkRenderer.NETWORKD
    assert InterfaceName("0123456789abcd") == "0123456789abcd"
    try:
        assert InterfaceName("0123456789abcdefg") == "This should not work"
    except ValueError:
        assert True
