from dataclasses import dataclass, field, fields
from pathlib import Path
from pprint import pprint
from typing import Dict, List, Optional, Union

import yaml

from mimir.interfaces.l2.dummy import Dummy

from mimir.interfaces.base import Base
from mimir.interfaces.l2.bond import Bond
from mimir.interfaces.l2.bridge import Bridge
from mimir.interfaces.l2.ethernet import Ethernet
from mimir.interfaces.l2.vlan import VLAN
from mimir.interfaces.l2.vrf import VRF
from mimir.interfaces.l2.vxlan import VXLAN
from mimir.interfaces.typing import InterfaceName, NetworkRenderer, Version


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
            nameservers:
                addresses:
                - 10.90.24.1
                - 10.90.24.17
                search:
                - sa2.ba.schiff.telekom.de
                - schiff.telekom.de
                - das-schiff.telekom.de
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
            description: "The Root of all hell"
            vrf: default
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
    additionals:
        10-default:
            - Match:
                - OriginalName: "vx*"
            - Link:
                - NamePolicy: "keep kernel database onboard slot path"
                - AlternativeNamesPolicy: "database onboard slot path"
                - MACAddressPolicy: "none"
        lo:
            - Match:
                - Name: "lo"
            - Network:
                - DHCP: "no"
                - IPv6AcceptRA: "no"
                - Address: "192.168.0.45/32"
        eth0:
            - Match:
                - Name: "eth0"
            - Network:
                - DHCP: "no"
                - IPv6AcceptRA: "no"
                - DNS: 8.8.8.8
                - DNS: 8.8.4.4
                - Domains: "telekom.local"
                - Address: "10.0.2.2/24"
                - Gateway: "10.0.2.15"
        eth1:
            - Match:
                - Name: "eth1"
            - Network:
                - VRF: "tenant_vrf"
                - DHCP: "no"
                - IPv6AcceptRA: "yes"
                - LinkLocalAddressing: "ipv6"
                - LLDP: "routers-only"
                - EmitLLDP: "yes"
                - LinkLocalAddressing: "ipv6"
                # - Address: "fd03:0:a802::73/127"
        eth2:
            - Match:
                - Name: "eth2"
            - Network:
                - VRF: "tenant_vrf"
                - DHCP: "no"
                - IPv6AcceptRA: "yes"
                - LLDP: "routers-only"
                - EmitLLDP: "yes"
                - LinkLocalAddressing: "ipv6"
                # - Address: "fd03:0:a802::75/127"
        tenant_vrf: 
            - Match:
                - Name: "tenant_vrf"
        br-vxl10:  
            - Match:
                - Name: "br-vxl10"
            - Network:
                - VRF: "tenant_vrf"
                - VXLAN: "vxl10"
                - LinkLocalAddressing: "no"
        vxl10:
            - Match: 
                - Name: "vxl10"
            
        tenant_vrf:
            - NetDev: 
                - Name: "tenant_vrf"
                - Kind: "vrf"
            - VRF:
                - Table: "5000"
        vxl10: 
            - NetDev:
                - Name: "vxl10"
                - Kind: "vxlan"
            - VXLAN:
                - Id: "5000" # The VXLAN ID to use
                - DestinationPort: "4789" # DestinationPort**
                - Local: 192.168.0.45
                - MacLearning: "no"
        br-vxl10:
            - NetDev:
                - Name: "br-vxl10"
                - Kind: "bridge"
            - Bridge:
                - STP: "no"
"""


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


if __name__ == "__main__":
    config = NetplannerConfig.from_dict(yaml.safe_load(worker_config))
    pprint(config)
    pprint(config.network.lookup("vx.5000"))
    # print(json.dumps(config.as_dict(), indent=2))
    assert config.network.renderer == NetworkRenderer.NETWORKD
    assert InterfaceName("0123456789abcd") == "0123456789abcd"
    try:
        assert InterfaceName("0123456789abcdefg") == "This should not work"
    except ValueError:
        assert True
