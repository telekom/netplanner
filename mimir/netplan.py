from dataclasses import dataclass, field
from typing import Dict

from .interfaces.base import Base, InterfaceName, NetworkRenderer, Version
from .interfaces.l2.bridge import Bridge
from .interfaces.l2.ethernet import Ethernet
from .interfaces.l2.vlan import VLAN
from .interfaces.l2.vxlan import VXLAN
from .interfaces.l2.vrf import VRF
from .interfaces.l2.bond import Bond
from pprint import pprint
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
    bonds:
        bond-uplink:
            mtu: 9000
            dhcp4: false
            dhcp6: false
            interfaces:
            - ens1f0
            - ens1f1
            parameters:
                mode: active-backup
                primary: ens1f0
    ethernets:
        ens1f0: {}
        ens1f1: {}
        ens2f0:
            mtu: 9100
            dhcp4: false
            dhcp6: false
            addresses:
            - "{{ ds.meta_data.storage_0 }}/{{ ds.meta_data.storage_prefix_0 }}"
        ens2f1:
            mtu: 9100
            dhcp4: false
            dhcp6: false
            addresses:
            - "{{ ds.meta_data.storage_1 }}/{{ ds.meta_data.storage_prefix_0 }}"
        
    version: 3
    renderer: networkd
    vlans:
        vlan.2259:
            addresses:
            - "{{ ds.meta_data.ip_0 }}/{{ ds.meta_data.prefix_0 }}"
            gateway4: "{{ ds.meta_data.gateway_0 }}"
            dhcp4: false
            mtu: 1500
            id: 2259
            link: bond-uplink
            nameservers:
                addresses:
                - 10.90.24.1
                - 10.90.24.17
                search:
                - sa2.ba.schiff.telekom.de
                - schiff.telekom.de
                - das-schiff.telekom.de
        vlan.2260:
            addresses:
            - "{{ ds.meta_data.ip_1 }}/{{ ds.meta_data.prefix_1 }}"
            #gateway4: "{{ ds.meta_data.gateway_1 }}"
            dhcp4: false
            mtu: 1500
            id: 2260
            link: bond-uplink
            nameservers:
                addresses:
                - 10.90.24.1
                - 10.90.24.17
                search:
                - sa2.ba.schiff.telekom.de
                - schiff.telekom.de
                - das-schiff.telekom.de
        vlan.2313:
            addresses:
            - "{{ ds.meta_data.ip_2 }}/{{ ds.meta_data.prefix_2 }}"
            #gateway4: "{{ ds.meta_data.gateway_2 }}"
            dhcp4: false
            mtu: 1500
            id: 2313
            link: bond-uplink
            nameservers:
                addresses:
                - 10.90.24.1
                - 10.90.24.17
                search:
                - sa2.ba.schiff.telekom.de
                - schiff.telekom.de
                - das-schiff.telekom.de
        vlan.2314:
            addresses:
            - "{{ ds.meta_data.ip_3 }}/{{ ds.meta_data.prefix_3 }}"
            #gateway4: "{{ ds.meta_data.gateway_3 }}"
            dhcp4: false
            mtu: 1500
            id: 2314
            link: bond-uplink
            nameservers:
                addresses:
                - 10.90.24.1
                - 10.90.24.17
                search:
                - sa2.ba.schiff.telekom.de
                - schiff.telekom.de
                - das-schiff.telekom.de
"""
@dataclass(frozen=True)
class NetworkConfig(Base):
    version: Version
    renderer: NetworkRenderer
    ethernets: Dict[InterfaceName, Ethernet] = field(default_factory=dict)
    bridges: Dict[InterfaceName, Bridge] = field(default_factory=dict)
    vxlans: Dict[InterfaceName, VXLAN] = field(default_factory=dict)
    bonds: Dict[InterfaceName, Bond] = field(default_factory=dict)
    vlans: Dict[InterfaceName, VLAN] = field(default_factory=dict)
    vrfs: Dict[InterfaceName, VRF] = field(default_factory=dict)

@dataclass(frozen=True)
class NetplanConfig(Base):
    network: NetworkConfig

if __name__ == "__main__":
    import yaml
    config = NetplanConfig.from_dict(
        yaml.safe_load(worker_config)
    )
    pprint(config)
    print(config.as_dict())
    assert config.network.renderer == NetworkRenderer.NETWORKD
    assert InterfaceName("0123456789abcd") == "0123456789abcd"
    try:
        assert InterfaceName("0123456789abcdefg") == "This should not work"
    except ValueError:
        assert True