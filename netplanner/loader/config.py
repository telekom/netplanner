import logging
import yaml
from typing import Optional
from pathlib import Path
from .util import merge_dicts


class ConfigLoader:

    logger = logging.getLogger("config_loader")
    DEFAULT_CONF_DIR = Path("/etc/netplanner/")
    NETPLAN_DEFAULT_CONF_DIR = Path("/etc/netplan/")

    def __init__(self, config: Optional[str] = None):
        self._internal_config: dict = {}
        self._is_netplan: bool = False
        self.path: Optional[Path] = None
        if config is None:
            if self.DEFAULT_CONF_DIR.exists():
                self.path = self.DEFAULT_CONF_DIR
            elif self.NETPLAN_DEFAULT_CONF_DIR.exists():
                self._is_netplan = True
                self.path = self.NETPLAN_DEFAULT_CONF_DIR
        else:
            path = Path(config)
            if path.exists():
                self.path = path
        if self.path is None:
            raise Exception(
                f"No configuration file/directory found tried [{self.DEFAULT_CONF_DIR}, {self.NETPLAN_DEFAULT_CONF_DIR}, {config}]"
            )

    def _load_file(self, path: Path):
        with open(path, "r") as file:
            return yaml.safe_load(file)

    def load_config(self) -> bool:
        if self.path.is_file():
            self._internal_config = self._load_file(self.path)
        else:
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
            loaded_configs = [self._load_file(path) for path in config_file_list]
            self._internal_config = merge_dicts(loaded_configs)
        return self._internal_config is not None

    @property
    def is_netplan(self) -> bool:
        return self._is_netplan

    @property
    def config(self) -> Optional[dict]:
        return self._internal_config
