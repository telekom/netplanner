from dataclasses import asdict
import dacite
from enum import Enum


class Base:
    @classmethod
    def from_dict(cls, data: dict, config=None):
        if config is None:
            return dacite.from_dict(data_class=cls, data=data)
        return dacite.from_dict(data_class=cls, data=data, config=config)

    def as_dict(self):
        return asdict(self)


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
