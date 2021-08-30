from dataclasses import dataclass, field
from typing import Dict, Optional

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
    ethernets:
        lo:
            link-local: []
            addresses:
                - 192.168.0.45/32
        ens1f0:
            link-local: ["ipv6"]
            emit-lldp: true
            virtual-function-count: 16
        ens1f1:
            link-local: ["ipv6"]
            emit-lldp: true
            virtual-function-count: 16
        ens2f0:
            link-local: ["ipv6"]
            emit-lldp: true
            virtual-function-count: 16
        ens2f1:
            link-local: ["ipv6"]
            emit-lldp: true
            virtual-function-count: 16
    version: 3
    renderer: networkd
    vrfs:
        Vrf_customer01:
            table: 5000
    vxlans:
        vx.5000:
            vrf: Vrf_customer01
            parameters:
                vni: 5000
                #default destination-port: 4789
                local: 192.168.0.45
                mac-learning: false
    bridges:
        br.5000:
            nameservers: {}
            parameters:
                stp: false
            vrf: Vrf_customer01
            interfaces:
                - vx.5000
"""


@dataclass(frozen=True)
class NetworkConfig(Base):
    version: Version
    renderer: NetworkRenderer
    ethernets: Dict[InterfaceName, Ethernet]
    bridges: Optional[Dict[InterfaceName, Bridge]]
    vxlans: Optional[Dict[InterfaceName, VXLAN]]
    bonds: Optional[Dict[InterfaceName, Bond]]
    vlans: Optional[Dict[InterfaceName, VLAN]]
    vrfs: Optional[Dict[InterfaceName, VRF]]


@dataclass(frozen=True)
class NetplanConfig(Base):
    network: NetworkConfig


if __name__ == "__main__":
    import yaml

    config = NetplanConfig.from_dict(yaml.safe_load(worker_config))
    pprint(config)
    print(json.dumps(config.as_dict(), indent=2))
    assert config.network.renderer == NetworkRenderer.NETWORKD
    assert InterfaceName("0123456789abcd") == "0123456789abcd"
    try:
        assert InterfaceName("0123456789abcdefg") == "This should not work"
    except ValueError:
        assert True
