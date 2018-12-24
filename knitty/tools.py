import yaml
import re
from typing import Tuple, Union

yaml_regex = re.compile(r'(?:^|\n)---\n(.+?\n)(?:---|\.\.\.)(?:\n|$)', re.DOTALL)


def load_yaml(string: Union[str, None], del_yaml: bool=False) -> Tuple[
    Union[str, None],
    Union[dict, list, str, None]
]:
    """
    returns (str_without_first_yaml_maybe, loaded_first_yaml)
    """
    if isinstance(string, str):
        found = yaml_regex.search(string)
        if found:
            return (yaml_regex.sub('\n\n', string, 1) if del_yaml else string,
                    yaml.load(found.group(1)))
        else:
            return string, None
    return None, None
