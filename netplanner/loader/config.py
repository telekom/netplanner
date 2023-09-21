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

import logging
from pathlib import Path
from typing import Optional

import yaml

from .util import merge_dicts


class ConfigLoader:
    logger = logging.getLogger("config_loader")
    DEFAULT_CONF_DIR = Path("/etc/netplanner/")
    NETPLAN_DEFAULT_CONF_DIR = Path("/etc/netplan/")

    def __init__(self, config: Optional[str] = None):
        self._internal_config: dict = {}
        self._is_netplan: bool = False
        self._path: Optional[Path] = None
        if config is None:
            if self.DEFAULT_CONF_DIR.exists():
                self.path = self.DEFAULT_CONF_DIR
            elif self.NETPLAN_DEFAULT_CONF_DIR.exists():
                self._is_netplan = True
                self.path = self.NETPLAN_DEFAULT_CONF_DIR
        else:
            self.path = Path(config)

    @property
    def path(self) -> Path:
        if self._path is None:
            raise ValueError(
                f"No configuration file/directory found tried [{self.DEFAULT_CONF_DIR}, {self.NETPLAN_DEFAULT_CONF_DIR}, {self._path}]"
            )
        return self._path

    @path.setter
    def path(self, value: Path):
        assert isinstance(value, Path)
        if value.exists():
            self._path = value

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
