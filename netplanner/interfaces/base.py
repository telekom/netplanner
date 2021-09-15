from dataclasses import asdict, dataclass
from enum import Enum
from ipaddress import (
    IPv4Address,
    IPv4Interface,
    IPv4Network,
    IPv6Address,
    IPv6Interface,
    IPv6Network,
)
from netplanner.interfaces.typing import (
    RouteScope,
    RouteType,
    TableShortInt,
    UnsignedShortInt,
)
from typing import Optional

import dacite
from fqdn import FQDN

from netplanner.interfaces.typing import (
    MTU,
    InterfaceName,
    LinkLocalAdressing,
    MacAddress,
    PositiveInt,
    VirtualFunctionCount,
    VLANId,
    VLANType,
)

RESERVED = ["from"]


@dataclass
class BaseSerializer:
    @staticmethod
    def streamline_keys(
        dictionary: dict,
        level: int = 0,
        old_char: str = "-",
        new_char: str = "_",
        ignore_levels: list = [2],
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
                ] = BaseSerializer.streamline_keys(
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
            else str(value)
            if isinstance(value, str)
            else int(value)
            if isinstance(value, int)
            else value
        )

    @staticmethod
    def to_complex_serializable(data):
        return (
            [BaseSerializer.to_complex_serializable(item) for item in data]
            if isinstance(data, (list, set))
            else {
                BaseSerializer.to_serializable(
                    key
                ): BaseSerializer.to_complex_serializable(val)
                for key, val in data.items()
            }
            if isinstance(data, dict)
            else BaseSerializer.to_serializable(data)
        )

    @staticmethod
    def dict_factory(data):
        return {
            field: BaseSerializer.to_complex_serializable(value)
            for field, value in data
        }

    @classmethod
    def from_dict(cls, data: dict):
        data = (
            BaseSerializer.streamline_keys(data)
            if cls.__name__ == "NetplannerConfig"
            else data
        )
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
                    UnsignedShortInt,
                    TableShortInt,
                    RouteType,
                    RouteScope,
                    LinkLocalAdressing,
                    FQDN,
                    MTU,
                    set,
                    IPv4Network,
                    IPv6Network,
                    IPv4Interface,
                    IPv6Interface,
                    IPv4Address,
                    IPv6Address,
                    VLANType,
                    VLANId,
                ],
                check_types=True,
                strict=True,
                strict_unions_match=True,
            ),
        )

    def as_dict(self):
        return BaseSerializer.streamline_keys(
            asdict(self, dict_factory=BaseSerializer.dict_factory),
            old_char="_",
            new_char="-",
        )

    @property
    def object_name(self) -> str:
        return self.__class__.__name__


@dataclass
class Base(BaseSerializer):
    description: Optional[str]
