from dataclasses import dataclass, field
from typing import Dict

from mimir.interfaces.l2.vf import VF

from .interfaces.base import Base, InterfaceName, NetworkRenderer, Version
from .interfaces.l2.bridge import Bridge
from .interfaces.l2.ethernet import Ethernet
from .interfaces.l2.vlan import VLAN
from .interfaces.l2.vxlan import VXLAN


@dataclass
class NetplanConfig(Base):
    version: Version
    renderer: NetworkRenderer
    ethernets: Dict[InterfaceName, Ethernet] = field(default_factory=dict)
    bridges: Dict[InterfaceName, Bridge] = field(default_factory=dict)
    vxlans: Dict[InterfaceName, VXLAN] = field(default_factory=dict)
    vlans: Dict[InterfaceName, VLAN] = field(default_factory=dict)
    vfs: Dict[InterfaceName, VF] = field(default_factory=dict)


if __name__ == "__main__":
    config = NetplanConfig.from_dict(
        {
            "version": 3,
            "renderer": "networkd",
            "bridges": {"br0": {"parameters": {}, "interfaces": []}},
        }
    )
    print(config)
    print(config.as_dict())
    assert config.renderer == NetworkRenderer.NETWORKD
    assert InterfaceName("0123456789abcd") == "0123456789abcd"
    try:
        assert InterfaceName("0123456789abcdefg") == "This should not work"
    except ValueError:
        assert True
