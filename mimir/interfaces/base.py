from dataclasses import asdict, dataclass
from enum import Enum
from ipaddress import (
    IPv4Address,
    IPv6Address,
    IPv6Network,
    IPv4Network,
    IPv4Interface,
    IPv6Interface,
)

import ipaddress
from typing import Set

import dacite
import re

from fqdn import FQDN

RESERVED = ["from"]


class Base:
    @staticmethod
    def streamline_keys(
        dictionary: dict,
        level: int = 0,
        old_char: str = "-",
        new_char: str = "_",
        ignore_levels: list = [2],
        read: bool = True,
    ) -> dict:
        keys = list(dictionary.keys())
        for key in keys:
            if isinstance(dictionary[key], dict):
                dictionary[
                    # This handles awkward netplan compatibility issues
                    # it excluded interface-names at the first level
                    f"_{key}"
                    if key in RESERVED
                    else key.replace("_", "", 1)
                    if key.startswith("_")
                    else key.replace(old_char, new_char)
                    if level not in ignore_levels
                    else key
                ] = Base.streamline_keys(
                    dictionary[key],
                    level=level + 1,
                    old_char=old_char,
                    new_char=new_char,
                    ignore_levels=ignore_levels,
                )
            else:
                dictionary[
                    # This handles awkward netplan compatibility issues
                    # it excluded interface-names at the first level
                    f"_{key}"
                    if key in RESERVED
                    else key.replace("_", "", 1)
                    if key.startswith("_")
                    else key.replace(old_char, new_char)
                    if level not in ignore_levels
                    else key
                ] = dictionary.pop(key)
        return dictionary

    @staticmethod
    def to_serializable(value):
        return (
            value.value
            if isinstance(value, Enum)
            else str(value)
            if isinstance(
                value,
                (
                    IPv4Network,
                    IPv6Network,
                    IPv4Interface,
                    IPv6Interface,
                    IPv4Address,
                    IPv6Address,
                ),
            )
            else value.relative
            if isinstance(value, FQDN)
            else value
        )

    @staticmethod
    def dict_factory(data):
        return {
            field: (
                [Base.to_serializable(item) for item in value]
                if isinstance(value, (list, set))
                else Base.to_serializable(value)
            )
            for field, value in data
        }

    @classmethod
    def from_dict(cls, data: dict):
        print(cls.__name__)
        data = Base.streamline_keys(data) if cls.__name__ == "NetplanConfig" else data
        print(data)
        return dacite.from_dict(
            data_class=cls,
            data=data,
            config=dacite.Config(
                cast=[
                    Enum,
                    InterfaceName,
                    MacAddress,
                    VirtualFunctionCount,
                    PositiveInt,
                    FQDN,
                    MTU,
                    IPv4Network,
                    IPv6Network,
                    IPv4Interface,
                    IPv6Interface,
                    IPv4Address,
                    IPv6Address,
                ],
                check_types=True,
                strict=True,
                strict_unions_match=True,
            ),
        )

    def as_dict(self):
        return Base.streamline_keys(
            asdict(self, dict_factory=Base.dict_factory), old_char="_", new_char="-"
        )

    def object_name(self) -> str:
        return self.__class__.__name__


class Version(Enum):
    THIRD = 3
    SECOND = 2


class NetworkRenderer(Enum):
    NETWORKD = "networkd"


class MTU(int):
    def __new__(cls, value: int):
        if not (256 <= value <= 9166):
            raise ValueError(f"MTUBytes={value} not in 256 - 9166")
        return super().__new__(cls, value)


class VirtualFunctionCount(int):
    def __new__(cls, value: int):
        if not (0 <= value <= 255):
            raise ValueError(f"VirtualFunctionCount={value} not in 0 - 255")
        return super().__new__(cls, value)


class PositiveInt(int):
    def __new__(cls, value: int):
        if not value >= 0:
            raise ValueError(f"PositiveInteger={value} < 0")
        return super().__new__(cls, value)


class InterfaceName(str):
    def __new__(cls, content: str):
        if len(content) > 15 or not content.isascii():
            raise ValueError(
                f"InterfaceName {content} of len {len(content)} not supported in Linux"
            )
        return super().__new__(cls, content)


class LinkLocalAdressing(str):
    def __new__(cls, content: str):
        if content not in ["ipv4", "ipv6"]:
            raise ValueError(f"LinkLocal={content} not in ['ipv4', 'ipv6']")
        return super().__new__(cls, content)


hex_re = re.compile(r"^[\da-f]+$")


class MacAddress(str):
    def __new__(cls, content: str):
        if len(content) != 17:
            raise ValueError(
                f"MacAddress {content} of len {len(content)} not supported in Linux"
            )
        if len(content.split(":")) != 6:
            raise ValueError(f"MacAddress {content} has not enough : or to many.")
        if not all([hex_re.match(item) for item in content.split(":")]):
            raise ValueError(f"MacAddress {content} malformed.")

        return str.__new__(cls, content)


@dataclass
class MatchObject(Base):
    name: InterfaceName
    macaddress: MacAddress
