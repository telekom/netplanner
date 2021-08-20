from dataclasses import asdict, dataclass, fields
from enum import Enum
from ipaddress import IPv4Address, IPv4Network, IPv6Address, IPv6Network
import ipaddress

import dacite
import re

RESERVED = ["from"]


class Base:
    @staticmethod
    def to_ip(value: str):
        try:
            return ipaddress.ip_network(value)
        except:
            pass
        return value
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
    def dict_factory(data):
        return {
            field: value.value
            if isinstance(value, Enum)
            else [
                str(item)
                if isinstance(
                    item, (IPv4Network, IPv6Network),
                )
                else item
                for item in value
            ]
            if isinstance(value, list)
            else value
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
                type_hooks={
                    str: Base.to_ip
                },
                cast=[
                    Enum,
                    InterfaceName,
                    MacAddress,
                    IPv6Network,
                    IPv4Network
                ],
                check_types=True,
                strict=True,
                strict_unions_match=False,
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


class NetworkRenderer(Enum):
    NETWORKD = "networkd"


class InterfaceName(str):
    def __new__(cls, content: str):
        if len(content) > 15 or not content.isascii():
            raise ValueError(
                f"InterfaceName {content} of len {len(content)} not supported in Linux"
            )
        return str.__new__(cls, content)


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
