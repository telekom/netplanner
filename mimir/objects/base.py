from dataclasses import asdict, dataclass
import dacite
from enum import Enum

from dacite import data


class Base:
    @staticmethod
    def dict_factory(data):
        return {
            field: value.value if isinstance(value, Enum) else value
            for field, value in data
        }
    @classmethod
    def from_dict(cls, data: dict):
        return dacite.from_dict(data_class=cls, data=data, config=dacite.Config(
                cast=[
                    Enum,
                    InterfaceName
                ]
            ),)

    def as_dict(self):
        return asdict(self, dict_factory=Base.dict_factory)


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
