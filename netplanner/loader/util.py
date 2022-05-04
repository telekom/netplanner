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
