import os
import os.path as p
import yaml
import re
from typing import Tuple, Union, Iterable

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


def where(executable: str, search_dirs: Iterable[str]=None) -> str:
    """
    :param executable: exec name without .exe
    :param search_dirs: extra dirs to look for executables
    :return: On Windows: absolute path to the exec that was found
      in the search_dirs or in the $PATH.
      On Unix: absolute path to the exec that was found in the search_dirs
      or executable arg unchanged.
    """
    def exe(_exe): return f'{_exe}.exe' if (os.name == 'nt') else _exe
    def is_exe(_exe): return True if (os.name == 'nt') else os.access(_exe, os.X_OK)

    for _dir in (search_dirs if search_dirs else ()):
        _exec = p.normpath(p.join(_dir, exe(executable)))
        if p.isfile(_exec):
            if is_exe(_exec):
                return p.abspath(_exec)

    if os.name == 'nt':
        from subprocess import run, PIPE

        exec_abs = run(
            [p.expandvars(r'%WINDIR%\System32\where.exe'), f'$PATH:{executable}.exe'],
            stdout=PIPE, encoding='utf-8',
        ).stdout.split('\n')[0].strip('\r')

        if p.isfile(exec_abs):
            return exec_abs
        else:
            raise KnittyError(f"'{executable}' wasn't found in the {search_dirs} and in the $PATH.")
    else:
        return executable
