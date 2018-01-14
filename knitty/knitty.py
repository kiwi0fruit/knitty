import sys
from .ast_filter import knitty_pandoc_filter
import click
import os
import re


def hyphenized_basename(file_path: str) -> str:
    return os.path.basename(file_path).replace('.', '-')


def dir_ext(to):
    """Takes first letter-word only. Replaces markdown dialects with 'md', None with 'html'."""
    if to is None:
        return 'html'
    formats = {'commonmark': 'md', 'markdown': 'md', 'gfm': 'md'}
    m = re.search(r'^[A-Za-z]+', to)
    if m:
        return formats.get(m.group(0), m.group(0))
    else:
        raise StitchError('Invalid -t/-w/--to/--write option: {}'.format(to))


@click.command(
    context_settings=dict(ignore_unknown_options=True,
                          allow_extra_args=True),
    help="Knitty is a Pandoc filter with arguments. It reads from stdin and writes to stdout." +
    "INPUT_FILE is optional but it helps to auto-name Knitty data folder in some cases."
)
@click.pass_context
@click.argument('input_file', type=str, default=None, required=False)
@click.option('-o', '--output', type=str, default=None,
              help='Pandoc writer option. Optional but it helps to auto-name Knitty data folder in some cases.')
@click.option('-w', '-t', '--write', '--to', type=str, default=None,
              help='Pandoc writer option. Optional but it helps to auto-name Knitty data folder in some cases.')
@click.option('--standalone', is_flag=True, default=False,
              help='Pandoc writer option. Produce a standalone document instead of fragment.')
@click.option('--self-contained', is_flag=True, default=False,
              help='Pandoc writer option. Store resources like images inside document instead of external files.')
@click.option('--dir-name', type=str, default=None,
              help='Manually name Knitty data folder (instead of default auto-naming).')
def main(ctx, input_file, output, to, standalone, self_contained, dir_name):
    if sys.stdin.isatty():
        raise Exception('The app is not meant to wait for user input.')

    if dir_name is None:
        if output is not None:
            dir_name = hyphenized_basename(output)
        elif input_file is not None:
            dir_name = hyphenized_basename(input_file) + '-' + dir_ext(to)
        else:
            dir_name = 'stdout-' + dir_ext(to)

    if to is not None:
        # Knitty (Stitch) later checks if `to` is in ('latex', 'pdf', 'beamer') so using `dir_ext` is OK
        to = dir_ext(to)
    else:
        ext = (os.path.splitext(output)[1].lstrip('.')
               if output is not None
               else '')
        to = ext if (ext != '') else 'html'
    
    pandoc_extra_args=ctx.args
    if standalone:
        pandoc_extra_args.append('--standalone')
    if self_contained:
        pandoc_extra_args.append('--self-contained')
    # Knitty (Stitch) later do not need `to` in `pandoc_extra_args` so loosing it is OK
    sys.stdout.write(knitty_pandoc_filter(sys.stdin.read(), name=dir_name, to=to, standalone=standalone,
                                          self_contained=self_contained, pandoc_extra_args=pandoc_extra_args))

if __name__ == '__main__':
    main()
