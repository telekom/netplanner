# netplanner
# Copyright (C) 2021-2023 Deutsche Telekom AG
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from dataclasses import dataclass, field, fields
from typing import Dict, List, OrderedDict, Union

from .interfaces.base import Base
from .interfaces.l2.bond import Bond
from .interfaces.l2.bridge import Bridge
from .interfaces.l2.dummy import Dummy
from .interfaces.l2.ethernet import Ethernet
from .interfaces.l2.veth import Veth
from .interfaces.l2.vlan import VLAN
from .interfaces.l2.vrf import VRF
from .interfaces.l2.vxlan import VXLAN
from .interfaces.typing import InterfaceName, NetworkRenderer, Version


@dataclass
class NetworkConfig(Base):
    version: Version
    renderer: NetworkRenderer = NetworkRenderer("networkd")
    dummies: Dict[InterfaceName, Dummy] = field(default_factory=dict)
    ethernets: Dict[InterfaceName, Ethernet] = field(default_factory=dict)
    bridges: Dict[InterfaceName, Bridge] = field(default_factory=dict)
    vxlans: Dict[InterfaceName, VXLAN] = field(default_factory=dict)
    bonds: Dict[InterfaceName, Bond] = field(default_factory=dict)
    vlans: Dict[InterfaceName, VLAN] = field(default_factory=dict)
    vrfs: Dict[InterfaceName, VRF] = field(default_factory=dict)
    veths: OrderedDict[InterfaceName, Veth] = field(default_factory=OrderedDict)
    additionals: Dict[str, List] = field(default_factory=dict)

    def lookup(
        self, name: InterfaceName
    ) -> Dict[
        InterfaceName, Union[Dummy, Ethernet, VXLAN, Bond, VLAN, VRF, Veth, List]
    ]:
        return {
            key: value
            for field in fields(self)
            if isinstance(getattr(self, field.name), dict)
            for key, value in getattr(self, field.name).items()
            if key == name
        }

    def __post_init__(self):
        for interface_name, interface_config in self.veths.items():
            if interface_config.link not in self.veths:
                raise ValueError(f"Link of Veth {interface_name} does not exist")
            if interface_config.link == interface_name:
                raise ValueError(
                    f"Link of Veth {interface_name} can not reference to itself"
                )
            if self.veths[interface_config.link].link != interface_name:
                raise ValueError(
                    f"Link of Veth {interface_name} does not have the same link"
                )
        self.veths = OrderedDict(sorted(self.veths.items()))


@dataclass
class NetplannerConfig(Base):
    network: NetworkConfig
