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

import re
from enum import Enum
from ipaddress import (
    IPv4Address,
    IPv4Interface,
    IPv4Network,
    IPv6Address,
    IPv6Interface,
    IPv6Network,
)
from typing import List, Union

IPInterfaceAddresses = List[Union[IPv4Interface, IPv6Interface]]
IPNetwork = Union[IPv4Network, IPv6Network]
IPAddress = Union[IPv4Address, IPv6Address]


class Version(Enum):
    THIRD = 3
    SECOND = 2


class NetworkRenderer(Enum):
    NETWORKD = "networkd"


class BondMode(Enum):
    ACTIVE_BACKUP = "active-backup"
    BALANCE_ROUND_ROBIN = "balance-rr"
    BALANCE_ROUND_ROBIN_EXCLUSIVE = "balance_xor"
    BALANCE_TLB = "balance-tlb"
    BALANCE_ALB = "balance-alb"
    BROADCAST = "broadcast"
    LACP = "802.3ad"


class BondADSelect(Enum):
    STABLE = "stable"
    BANDWITH = "bandwidth"
    COUNT = "count"


class BondTransmitHashPolicy(Enum):
    LAYER2 = "layer2"
    LAYER23 = "layer2+3"
    LAYER34 = "layer3+4"
    ENCAP23 = "encap2+3"
    ENCAP34 = "encap3+4"


class BondLACPRate(Enum):
    SLOW = "slow"
    FAST = "fast"


class MTU(int):
    def __new__(cls, value: int):
        if not (1280 <= value <= 9166):
            raise ValueError(f"MTUBytes={value} not in 1280(ipv6 minimum) - 9166")
        return super().__new__(cls, value)


class PositiveInt(int):
    def __new__(cls, value: int):
        if not value > 0:
            raise ValueError(f"PositiveInteger={value} <= 0")
        return super().__new__(cls, value)


class UnsignedShortInt(PositiveInt):
    def __new__(cls, value: int):
        if value > 255:
            raise ValueError(f"UnsignedShortInt={value} > 255")
        return super().__new__(cls, value)


class TableShortInt(UnsignedShortInt):
    reserved = {255: "local", 254: "main", 253: "default", 0: "unspec"}

    def __new__(cls, value: int):
        if value in cls.reserved.keys():
            raise ValueError(
                f"Table={value} in [{', '.join([f'{value}={key}' for key, value in cls.reserved.items()])}]"
            )
        return super().__new__(cls, value)


class InterfaceName(str):
    __supertype__ = str

    def __new__(cls, content: str):
        if len(content) > 15 or not content.isascii():
            raise ValueError(
                f"InterfaceName {content} of len {len(content)} not supported in Linux"
            )
        return super().__new__(cls, content)


class LinkLocalAdressing(str):
    __supertype__ = str

    def __new__(cls, content: str):
        if content not in ["ipv4", "ipv6"]:
            raise ValueError(f"LinkLocal={content} not in ['ipv4', 'ipv6']")
        return super().__new__(cls, content)


class VLANType(Enum):
    Q1802 = "802.1q"
    AD1802 = "802.1ad"


class VLANId(int):
    def __new__(cls, value: int):
        if value and not (2 <= value <= 4094):
            raise ValueError(f"VLAN Id={value} not in 2 - 4094")
        return super().__new__(cls, value)


class VirtualFunctionCount(int):
    def __new__(cls, value: int):
        if not (0 <= value <= 255):
            raise ValueError(f"VirtualFunctionCount={value} not in 0 - 255")
        return super().__new__(cls, value)


class MacAddress(str):
    __supertype__ = str
    hex_re = re.compile(r"^[\da-f]+$")

    def __new__(cls, content: str):
        if len(content) != 17:
            raise ValueError(
                f"MacAddress {content} of len {len(content)} not supported in Linux"
            )
        if len(content.split(":")) != 6:
            raise ValueError(f"MacAddress {content} has not enough : or to many.")
        if not all([MacAddress.hex_re.match(item) for item in content.split(":")]):
            raise ValueError(f"MacAddress {content} malformed.")

        return str.__new__(cls, content)

    def set_ip_bytes(cls, address: IPAddress) -> str:
        if not isinstance(address, IPv4Address):
            raise ValueError("IPv6 not supported for MAC generation")
        mac_bytes = bytearray.fromhex(cls.replace(":", ""))
        return MacAddress(bytes(mac_bytes[:2] + address.packed).hex(":"))


class RouteType(Enum):
    UNREACHABLE = "unreachable"
    BLACKHOLE = "blackhole"
    PROHIBIT = "prohibit"
    UNICAST = "unicast"


class RouteScope(Enum):
    GLOBAL = "global"
    LINK = "link"
    HOST = "host"


class ESwitchMode(Enum):
    LEGACY = "legacy"
    SWITCHDEV = "switchdev"
