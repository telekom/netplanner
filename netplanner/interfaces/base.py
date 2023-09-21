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

from dataclasses import asdict, dataclass
from enum import Enum
from ipaddress import (
    IPv4Address,
    IPv4Interface,
    IPv4Network,
    IPv6Address,
    IPv6Interface,
    IPv6Network,
    ip_address,
    ip_interface,
    ip_network,
)
from typing import Optional, OrderedDict, Union

import dacite
from fqdn import FQDN as UpstreamFQDN  # type: ignore

from .typing import (
    ESwitchMode,
    IPInterfaceAddresses,
    MTU,
    InterfaceName,
    LinkLocalAdressing,
    MacAddress,
    PositiveInt,
    RouteScope,
    RouteType,
    TableShortInt,
    UnsignedShortInt,
    VirtualFunctionCount,
    VLANId,
    VLANType,
)


class FQDN(UpstreamFQDN):
    def __str__(self):
        return self.relative


@dataclass
class BaseSerializer:
    @staticmethod
    def RESERVED() -> list[str]:
        return ["from"]

    @staticmethod
    def get_streamlined_key(
        key: str, level: int, old_char: str, new_char: str, ignore_levels: list
    ) -> str:
        """
        This handles awkward netplan compatibility issues.
        it excludes interface-names at the first level of the yaml configuration file
        """
        if key in BaseSerializer.RESERVED():
            return f"_{key}"
        elif key.startswith("_"):
            return key[1:]
        elif level not in ignore_levels:
            return key.replace(old_char, new_char)
        else:
            return key

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
            sanitized_key = BaseSerializer.get_streamlined_key(
                key,
                level=level,
                old_char=old_char,
                new_char=new_char,
                ignore_levels=ignore_levels,
            )
            match dictionary[key]:
                case dict():
                    dictionary[sanitized_key] = BaseSerializer.streamline_keys(
                        dictionary[key],
                        level=level + 1,
                        old_char=old_char,
                        new_char=new_char,
                        ignore_levels=ignore_levels,
                    )
                case _:
                    dictionary[sanitized_key] = dictionary.pop(key)
        return dictionary

    @staticmethod
    def to_serializable(value) -> Union[int, str]:
        match value:
            case Enum():
                return Base.to_serializable(value.value)
            case IPv4Network() | IPv6Network() | IPv4Interface() | IPv6Interface() | IPv4Address() | IPv6Address() | str():
                return str(value)
            case int():
                return int(value)
            case _:
                return value

    @staticmethod
    def to_complex_serializable(data) -> Union[list, dict, int, str]:
        match data:
            case list() | set():
                return [BaseSerializer.to_complex_serializable(item) for item in data]
            case dict():
                return {
                    BaseSerializer.to_serializable(
                        key
                    ): BaseSerializer.to_complex_serializable(val)
                    for key, val in data.items()
                }
            case _:
                return BaseSerializer.to_serializable(data)

    @staticmethod
    def dict_factory(data) -> dict[Union[str, int], Union[list, dict, int, str]]:
        return {
            BaseSerializer.to_serializable(
                field
            ): BaseSerializer.to_complex_serializable(value)
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
                    FQDN,
                    InterfaceName,
                    MacAddress,
                    VirtualFunctionCount,
                    ESwitchMode,
                    PositiveInt,
                    UnsignedShortInt,
                    TableShortInt,
                    RouteType,
                    RouteScope,
                    LinkLocalAdressing,
                    OrderedDict,
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
                type_hooks={
                    IPInterfaceAddresses: lambda x: [ip_interface(y) for y in x],
                    IPv4Network: ip_network,
                    IPv6Network: ip_network,
                    IPv4Address: ip_address,
                    IPv6Address: ip_address,
                },
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
