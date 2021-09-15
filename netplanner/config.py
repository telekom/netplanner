from dataclasses import dataclass, field, fields
from typing import Dict, List, Union

from netplanner.interfaces.base import Base
from netplanner.interfaces.l2.bond import Bond
from netplanner.interfaces.l2.bridge import Bridge
from netplanner.interfaces.l2.dummy import Dummy
from netplanner.interfaces.l2.ethernet import Ethernet
from netplanner.interfaces.l2.vlan import VLAN
from netplanner.interfaces.l2.vrf import VRF
from netplanner.interfaces.l2.vxlan import VXLAN
from netplanner.interfaces.typing import InterfaceName, NetworkRenderer, Version


@dataclass
class NetworkConfig(Base):
    version: Version
    renderer: NetworkRenderer
    dummies: Dict[InterfaceName, Dummy] = field(default_factory=dict)
    ethernets: Dict[InterfaceName, Ethernet] = field(default_factory=dict)
    bridges: Dict[InterfaceName, Bridge] = field(default_factory=dict)
    vxlans: Dict[InterfaceName, VXLAN] = field(default_factory=dict)
    bonds: Dict[InterfaceName, Bond] = field(default_factory=dict)
    vlans: Dict[InterfaceName, VLAN] = field(default_factory=dict)
    vrfs: Dict[InterfaceName, VRF] = field(default_factory=dict)
    additionals: Dict[str, List] = field(default_factory=dict)

    def lookup(
        self, name: InterfaceName
    ) -> Dict[InterfaceName, Union[Dummy, Ethernet, VXLAN, Bond, VLAN, VRF, List]]:
        return {
            key: value
            for field in fields(self)
            if isinstance(getattr(self, field.name), dict)
            for key, value in getattr(self, field.name).items()
            if key == name
        }


@dataclass
class NetplannerConfig(Base):
    network: NetworkConfig
