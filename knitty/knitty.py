import sys
from .ast_filter import knitty_pandoc_filter
import click
import os
import os.path as p
import re
import panflute as pf
import io
from .consts import PANDOC_CODECELL_CLASSES
from .tools import KnittyError


def hyphenized_basename(file_path: str) -> str:
    return p.basename(file_path).replace('.', '-')


def dir_ext(to):
    """Takes first letter-word only. Replaces markdown dialects with 'md', None with 'html'."""
    if to is None:
        return 'html'
    formats = {'commonmark': 'md', 'markdown': 'md', 'gfm': 'md'}
    m = re.search(r'^[A-Za-z]+', to)
    if m:
        return formats.get(m.group(0), m.group(0))
    else:
        raise KnittyError(f'Invalid -t/-w/--to/--write option: {to}')


@click.command(
    context_settings=dict(ignore_unknown_options=True,
                          allow_extra_args=True),
    help=("Knitty is a Pandoc AST filter with options. It reads from stdin and writes to stdout. "
          "It accepts all possible pandoc options and two knitty-only options. "
          "FILTER_TO is a stripped output format passed py Pandoc to it's filters. "
          "INPUT_FILE is optional but it helps to auto-name Knitty data folder in some cases.")
)
@click.pass_context
@click.argument('filter_to', type=str, required=True)
@click.argument('input_file', type=str, default=None, required=False)
@click.option('-f', '-r', '--from', '--read', 'read', type=str, default="markdown",
              help='Pandoc reader option. Specify input format.')
@click.option('-o', '--output', type=str, default=None,
              help='Pandoc writer option. Optional but it helps to auto-name Knitty data folder in some cases.')
@click.option('-w', '-t', '--write', '--to', 'to', type=str, default=None,
              help="Pandoc writer option. Optional but it helps to auto-name Knitty data folder in some cases. " +
              "Also the `-t` and `-o` options -> extension -> passed to Stitch that uses it in: " +
              "`if self.to in ('latex', 'pdf', 'beamer')`.")
@click.option('--standalone', is_flag=True, default=False,
              help='Pandoc writer option. Produce a standalone document instead of fragment. ' +
              'The option is added to `pandoc_extra_args` given to Stitch.')
@click.option('--self-contained', is_flag=True, default=False,
              help='Pandoc writer option. Store resources like images inside document instead of external files. ' +
              'The option is added to `pandoc_extra_args` given to Stitch.')
@click.option('--dir-name', type=str, default=None,
              help='Manually name Knitty data folder (instead of default auto-naming).')
def main(ctx, filter_to, input_file, read, output, to, standalone, self_contained, dir_name):
    if dir_name is None:
        if output is not None:
            dir_name = hyphenized_basename(output)
        elif input_file is not None:
            dir_name = hyphenized_basename(input_file) + '-' + dir_ext(to)
        else:
            dir_name = 'stdout-' + dir_ext(to)

    if to is not None:
        # TODO Stitch later checks if `to` is in ('latex', 'pdf', 'beamer') so using `dir_ext` is OK
        to = dir_ext(to)
    else:
        ext = (p.splitext(output)[1].lstrip('.')
               if output is not None
               else '')
        to = ext if (ext != '') else 'html'

    pandoc_extra_args = ctx.args
    if standalone:
        pandoc_extra_args.append('--standalone')
    if self_contained:
        pandoc_extra_args.append('--self-contained')
    # TODO Stitch later do not need `to` in `pandoc_extra_args` so loosing it is OK
    out = knitty_pandoc_filter(sys.stdin.read(), name=dir_name, filter_to=filter_to, standalone=standalone,
                               self_contained=self_contained, pandoc_format=read,
                               pandoc_extra_args=pandoc_extra_args)

    # TODO after `dir_ext()` `to` is still 'ipynb':
    if to.lower() == 'ipynb':
        with io.StringIO(out) as f:
            doc = pf.load(f)
        pf.run_filter(action, doc=doc)
        with io.StringIO() as f:
            pf.dump(doc, f)
            out = f.getvalue()
    sys.stdout.write(out)


def action(elem, doc):
    if isinstance(elem, pf.CodeBlock):
        input_ = elem.attributes.get('input', doc.get_metadata('input'))
        if str(input_).lower() == 'true':
            for clss in PANDOC_CODECELL_CLASSES: 
                if clss not in elem.classes:
                    elem.classes.append(clss)


if __name__ == '__main__':
    main()
