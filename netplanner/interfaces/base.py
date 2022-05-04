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
from typing import Optional, OrderedDict, Union

import dacite
from fqdn import FQDN as UpstreamFQDN  # type: ignore

from .typing import (
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
            ## Python 3.10 code
            # match dictionary[key]:
            #     case dict():
            #         dictionary[sanitized_key] = BaseSerializer.streamline_keys(
            #             dictionary[key],
            #             level=level + 1,
            #             old_char=old_char,
            #             new_char=new_char,
            #             ignore_levels=ignore_levels,
            #         )
            #     case _:
            #         dictionary[sanitized_key] = dictionary.pop(key)
            if isinstance(dictionary[key], dict):
                dictionary[sanitized_key] = BaseSerializer.streamline_keys(
                    dictionary[key],
                    level=level + 1,
                    old_char=old_char,
                    new_char=new_char,
                    ignore_levels=ignore_levels,
                )
            else:
                dictionary[sanitized_key] = dictionary.pop(key)
        return dictionary

    @staticmethod
    def to_serializable(value) -> Union[int, str]:
        ## Python 3.10 code
        # match value:
        #     case Enum():
        #         return Base.to_serializable(value.value)
        #     case IPv4Network() | IPv6Network() | IPv4Interface() | IPv6Interface() | IPv4Address() | IPv6Address() | str():
        #         return str(value)
        #     case int():
        #         return int(value)
        #     case _:
        #         return value
        if isinstance(value, Enum):
            return Base.to_serializable(value.value)
        elif isinstance(
            value,
            (
                IPv4Network,
                IPv6Network,
                IPv4Interface,
                IPv6Interface,
                IPv4Address,
                IPv6Address,
                str,
            ),
        ):
            return str(value)
        elif isinstance(value, int):
            return int(value)
        else:
            return value

    @staticmethod
    def to_complex_serializable(data) -> Union[list, dict, int, str]:
        ## Python 3.10 code
        # match data:
        #     case list() | set():
        #         return [
        #             BaseSerializer.to_complex_serializable(item) for item in data
        #         ]
        #     case dict():
        #         return {
        #             BaseSerializer.to_serializable(
        #                 key
        #             ): BaseSerializer.to_complex_serializable(val)
        #             for key, val in data.items()
        #         }
        #     case _:
        #         return BaseSerializer.to_serializable(data)
        if isinstance(data, (list, set)):
            return [BaseSerializer.to_complex_serializable(item) for item in data]
        elif isinstance(data, dict):
            return {
                BaseSerializer.to_serializable(
                    key
                ): BaseSerializer.to_complex_serializable(val)
                for key, val in data.items()
            }
        else:
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
