import os
import os.path as p
from subprocess import run, PIPE
import re
import sys
import click
from typing import Iterable
from shutilwhich_cwdpatch import which
from ..tools import KnittyError


doc = '''---
panflute-filters: {}
...
x
'''.format(p.join(p.dirname(p.abspath(__file__)), 'pandoc_filter_arg', 'pandoc_filter_arg.py'))


def pandoc_filter_arg(output: str=None, to: str=None, search_dirs: Iterable[str]=None) -> str:
    """
    :param output: Pandoc writer option
    :param to: Pandoc writer option
    :param search_dirs: extra dirs to look for executables
    :return: argument that is passed by Pandoc to it's filters
        Uses Pandoc's defaults.
    """
    if search_dirs:
        path = os.environ.get("PATH", os.defpath)
        kwargs = dict(path=os.pathsep.join(search_dirs) + ((os.pathsep + path) if path else ''))
    else:
        kwargs = {}
    pandoc, panfl = which('pandoc', **kwargs), which('panfl', **kwargs)
    if not (pandoc and panfl):
        raise KnittyError("pandoc or panfl executable wasn't found")

    args = [pandoc, '-f', 'markdown', '--filter', panfl, '-o', (output if output else '-')]
    if to:
        args += ['-t', to]

    # Run subprocess that would definitely give error and get stderr:
    err = run(args, stderr=PIPE, input=doc.encode()).stderr
    err = err.decode() if err else ''

    match = None
    for match in re.findall(r'(?<=\$\$\$).+?(?=\$\$\$)', err):
        pass
    if match is None:
        raise KnittyError(f'stderr output to parse: {err}')
    else:
        return match


# noinspection PyUnusedLocal
@click.command(
    context_settings=dict(ignore_unknown_options=True,
                          allow_extra_args=True),
    help="CLI interface that prints argument that is passed by Pandoc to it's filters. " +
         "Uses Pandoc's defaults. Ignores extra arguments."
)
@click.pass_context
@click.option('-o', '--output', type=str, default=None,
              help='Pandoc writer option.')
@click.option('-w', '-t', '--write', '--to', 'to', type=str, default=None,
              help="Pandoc writer option.")
def cli(ctx, output, to):
    sys.stdout.write(pandoc_filter_arg(output, to))
