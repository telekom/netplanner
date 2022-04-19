import logging
import yaml
from typing import Optional, Union
from pathlib import Path
from .util import merge_dicts


class ConfigLoader:

    logger = logging.getLogger("config_loader")
    DEFAULT_CONF_DIR = Path("/etc/netplanner/")
    NETPLAN_DEFAULT_CONF_DIR = Path("/etc/netplan/")

    def __init__(self, config: Optional[Union[str, Path]] = None):
        self._internal_config: dict = {}
        self._is_netplan: bool = False
        self.path = config

    @property
    def path(self) -> Path:
        if self._path is None:
            raise Exception(
                f"No configuration file/directory found tried [{self.DEFAULT_CONF_DIR}, {self.NETPLAN_DEFAULT_CONF_DIR}, {self._path}]"
            )
        return self._path

    @path.setter
    def path(self, value: Optional[str]):
        self._path = None
        if value is None:
            if self.DEFAULT_CONF_DIR.exists():
                self._path = self.DEFAULT_CONF_DIR
            elif self.NETPLAN_DEFAULT_CONF_DIR.exists():
                self._is_netplan = True
                self._path = self.NETPLAN_DEFAULT_CONF_DIR
        else:
            path = Path(value)
            if path.exists():
                self._path = path

    @property
    def config_file_list(self) -> list[Path]:
        config_file_list = sorted(
            [
                path
                for path in self.path.iterdir()
                if path.is_file() and path.suffix in [".yaml", ".yml"]
            ],
            reverse=True,
        )
        if not config_file_list:
            raise Exception(f"Config Directory [{self.path}] is empty")
        return config_file_list

    def _load_file(self, path: Path):
        with open(path, "r") as file:
            return yaml.safe_load(file)

    def load_config(self) -> bool:
        if self.path.is_file():
            self._internal_config = self._load_file(self.path)
        else:
            loaded_configs = [self._load_file(path) for path in self.config_file_list]
            self._internal_config = merge_dicts(loaded_configs)
        return self._internal_config is not None

    @property
    def is_netplan(self) -> bool:
        return self._is_netplan

    @property
    def config(self) -> Optional[dict]:
        return self._internal_config
