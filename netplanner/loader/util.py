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

from functools import reduce
from typing import Optional


def merge(dict_a: dict, dict_b: dict, path: Optional[list[str]] = None) -> dict:
    if path is None:
        path = []
    for key in dict_b:
        if key in dict_a:
            if isinstance(dict_a[key], dict) and isinstance(dict_b[key], dict):
                merge(dict_a[key], dict_b[key], path=path + [str(key)])
            elif dict_a[key] == dict_b[key]:
                pass
            else:
                # Coflict resolution by letting dict_a always win.
                dict_a[key] = dict_a[key]
                # If Conflict should be implemented uncomment the next line.
                # raise Exception(f'Conflict at {".".join(path + [str(key)])}')
        else:
            dict_a[key] = dict_b[key]
    return dict_a


def merge_dicts(dicts: list[dict]) -> dict:
    return reduce(merge, dicts)
