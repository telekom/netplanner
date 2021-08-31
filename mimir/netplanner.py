from dataclasses import dataclass, field
from mimir.interfaces.l2.dummy import Dummy
from typing import Dict, Optional, Union

from .interfaces.base import Base
from .interfaces.typing import InterfaceName, NetworkRenderer, Version
from .interfaces.l2.bridge import Bridge
from .interfaces.l2.ethernet import Ethernet
from .interfaces.l2.vlan import VLAN
from .interfaces.l2.vxlan import VXLAN
from .interfaces.l2.vrf import VRF
from .interfaces.l2.bond import Bond
from pprint import pprint
import json
from pathlib import Path


local = "./"
networkd_path = Path(f"{local}etc/systemd/network")
if local:
    networkd_path.mkdir(parents=True, exist_ok=True)

master_config = """
# This is the network config written by 'subiquity'
network:
  vlans:
    vlan.2257:
      id: 2257
      link: bond-uplink
    #   dhcp4: true
    #   dhcp4-overrides:
    #     hostname: bac4
  bonds:
    bond-uplink:
      interfaces:
      - eno1
      - eno2
      parameters:
        mode: active-backup
        primary: eno1
    #   dhcp4: false
    #   dhcp6: false
  ethernets:
    eno1:
      virtual-function-count: 4
    #   dhcp4: false
    #   dhcp6: false
    eno2:
        optional: True
    #   dhcp4: false
    #   dhcp6: false
  renderer: networkd
  version: 3
"""
worker_config = """
network:
    dummies:
        dummy.underlay:
            link_local: []
            vrf: Vrf_underlay
            addresses:
                - 192.168.0.45/32
        dummy.cluster:
            link_local: []
            vrf: default
            addresses:
                - 172.23.166.150/32
    ethernets:  
        ens1f0:
            link-local: ["ipv6"]
            emit-lldp: true
            vrf: Vrf_underlay
            virtual-function-count: 16
        ens1f1:
            link-local: ["ipv6"]
            emit-lldp: true
            vrf: Vrf_underlay
            virtual-function-count: 16
        ens2f0:
            link-local: ["ipv6"]
            emit-lldp: true
            vrf: Vrf_underlay
            virtual-function-count: 16
        ens2f1:
            link-local: ["ipv6"]
            emit-lldp: true
            vrf: Vrf_underlay
            virtual-function-count: 16
    version: 3
    renderer: networkd
    vrfs:
        Vrf_underlay:
            table: 1
    vxlans:
        vx.5000:
            vrf: default
            link: dummy.underlay
            parameters:
                vni: 5000
                #default destination-port: 4789
                local: 192.168.0.45
                mac-learning: false
    bridges:
        br.cluster:
            nameservers: {}
            parameters:
                stp: false
            vrf: default
            interfaces:
                - vx.5000
"""


@dataclass(frozen=True)
class NetworkConfig(Base):
    version: Version
    renderer: NetworkRenderer
    dummies: Dict[InterfaceName, Dummy] = field(default_factory=dict)
    ethernets: Dict[InterfaceName, Ethernet] = field(default_factory=dict)
    bridges: Dict[InterfaceName, Bridge] = field(default_factory=dict)
    vxlans: Dict[InterfaceName, VXLAN] = field(default_factory=dict)
    bonds: Dict[InterfaceName, Bond]= field(default_factory=dict)
    vlans: Dict[InterfaceName, VLAN] = field(default_factory=dict)
    vrfs: Dict[InterfaceName, VRF] = field(default_factory=dict)

    def lookup(self, name: InterfaceName)-> Dict[InterfaceName, Union[Dummy, Ethernet, VXLAN, Bond, VLAN, VRF]]:
        return {key: value for field in self.__dataclass_fields__ if isinstance(getattr(self, field), dict) for key, value in getattr(self, field).items() if key == name}

@dataclass(frozen=True)
class NetplannerConfig(Base):
    network: NetworkConfig


if __name__ == "__main__":
    import yaml

    config = NetplannerConfig.from_dict(yaml.safe_load(worker_config))
    pprint(config)
    pprint(config.network.lookup('vx.5000'))
    # print(json.dumps(config.as_dict(), indent=2))
    assert config.network.renderer == NetworkRenderer.NETWORKD
    assert InterfaceName("0123456789abcd") == "0123456789abcd"
    try:
        assert InterfaceName("0123456789abcdefg") == "This should not work"
    except ValueError:
        assert True
