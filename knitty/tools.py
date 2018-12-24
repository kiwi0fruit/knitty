import yaml
import re
from typing import Tuple, Union

yaml_regex = re.compile(r'(?:^|\n)---\n(.+?\n)(?:---|\.\.\.)(?:\n|$)', re.DOTALL)


def load_yaml(string: Union[str, None], del_yaml: bool=False) -> Tuple[str, dict]:
    """
    returns (str_without_first_yaml_maybe, loaded_first_yaml)
    """
    if isinstance(string, str) and string:
        found = yaml_regex.search(string)
        if found:
            yml = yaml.load(found.group(1))
            if del_yaml:
                string = yaml_regex.sub('\n\n', string, 1)
            return string, (yml if isinstance(yml, dict) else {})
        else:
            return string, {}
    return '', {}
