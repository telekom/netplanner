from dataclasses import dataclass, field
from ipaddress import IPv4Address, IPv4Network, IPv6Address, IPv6Network
from typing import List, Optional, Union

from ..base import Base, InterfaceName, MacAddress
from ..l3.nameserver import NameServers
from ..l3.route import Route


@dataclass
class VXLANParameters(Base):
    vni: int
    remote: Optional[Union[IPv4Address, IPv6Address]]
    local: Union[IPv6Address, IPv4Address]
    group: Optional[Union[IPv4Address, IPv6Address]]
    tos: Optional[bytes]
    ttl: Optional[int]
    mac_learning: Optional[bool]
    fdb_ageing_sec: Optional[int]
    maximum_fdb_entries: Optional[int]
    l2_miss_notification: Optional[bool]
    l3_miss_notification: Optional[bool]
    route_short_circuit: Optional[bool]
    udp_checksum: Optional[bool]
    udp_6_zero_checksum_tx: Optional[bool]
    udp_6_zero_checksum_rx: Optional[bool]
    remote_checksum_tx: Optional[bool]
    remote_checksum_rx: Optional[bool]
    flow_label: Optional[int]
    ip_do_not_fragment: Optional[Union[bool]]
    destination_port: int = field(default=4789)
    generic_protocol_extension: bool = field(default=False)
    group_policy_extension: bool = field(default=False)
    reduce_arp_proxy: bool = field(default=False)
    
    def __post_init__(self):
        if self.flow_label and self.flow_label not in range(1048576):
            raise ValueError(
                f"VXLANParameters FlowLabel={self.flow_label} not in 0 - 1048575"
            )
        if self.destination_port not in range(65536):
            raise ValueError(
                f"VXLANParameters DestinationPort={self.destination_port} not in 0 - 65535"
            )
        if self.vni not in range(1, 16777216):
            raise ValueError(f"VXLANParameters VNI={self.vni} not in 1 - 16777215")
        if self.ttl and self.ttl not in range(256):
            raise ValueError(f"VXLANParameters TTL={self.ttl} not in 0 - 255")
        if self.tos and self.tos not in range(64):
            raise ValueError(f"VXLANParameters Tos={self.tos} not in 0 - 63")


@dataclass
class VXLAN(Base):
    parameters: VXLANParameters
    link: Optional[InterfaceName]
    nameservers: NameServers
    mtu: Optional[int]
    macaddress: Optional[MacAddress]
    vrf: InterfaceName = field(default=InterfaceName("default"))
    addresses: List[Union[IPv4Network, IPv6Network]] = field(default_factory=list)
    routes: List[Route] = field(default_factory=list)

    def __post_init__(self):
        if self.mtu and self.mtu not in range(256,9001):
            raise ValueError(f"VXLAN MTUBytes={self.mtu} not in 256 - 9000")