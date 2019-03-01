import yaml
import re
from typing import Tuple, Union

yaml_regex = re.compile(r'(?:^|\n)---\n(.+?\n)(?:---|\.\.\.)(?:\n|$)', re.DOTALL)


class KnittyError(Exception):
    pass


def load_yaml(string: Union[str, None], del_yaml: bool=False) -> Tuple[str, dict]:
    """
    returns (string_without_first_yaml, first_yaml_dict) if del_yaml
            else (string, first_yaml_dict)
    """
    if isinstance(string, str) and string:
        found = yaml_regex.search(string)
        if found:
            yml = yaml.load(found.group(1))
            if del_yaml:
                string = yaml_regex.sub('\n\n', string, 1)
            if not isinstance(yml, dict):
                yml = {}
            return string, yml
        else:
            return string, {}
    return '', {}


def get(maybe_dict, key: str, default=None):
    """returns ``default`` if ``maybe_dict`` is not a ``dict``"""
    return maybe_dict.get(key, default) if isinstance(maybe_dict, dict) else default


def strict_str(smth) -> str:
    """Converts not str objects to empty string"""
    return smth if smth and isinstance(smth, str) else ''
