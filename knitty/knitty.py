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


@click.command(
    context_settings=dict(ignore_unknown_options=True,
                          allow_extra_args=True),
    help=("Knitty is a Pandoc AST filter with options. It reads from stdin and writes to stdout. "
          "It accepts all possible pandoc options but the first arg should be "
          "FILTER_TO that is a stripped output format passed py Pandoc to it's filters. "
          "INPUT_FILE is optional but it helps to auto-name Knitty data folder if --output is absent.")
)
@click.pass_context
@click.argument('filter_to', type=str, required=True)
@click.argument('input_file', type=str, default=None, required=False)
@click.option('-f', '-r', '--from', '--read', 'read', type=str, default="markdown",
              help='Pandoc reader option. Specify input format. Affects Knitty parsing.')
@click.option('-o', '--output', type=str, default=None,
              help='Pandoc writer option. It ONLY helps to auto-name Knitty data folder.')
@click.option('-w', '-t', '--write', '--to', 'to', type=str, default=None,
              help="Pandoc writer option. Does nothing.")
@click.option('--standalone', is_flag=True, default=False,
              help='Pandoc writer option. Produce a standalone document instead of fragment. ' +
              'Affects Knitty behaviour and also is added to `pandoc_extra_args`.')
@click.option('--self-contained', is_flag=True, default=False,
              help='Pandoc writer option. Store resources like images inside document instead of external files. ' +
              'Affects Knitty behaviour and also is added to `pandoc_extra_args`.')
def main(ctx, filter_to, input_file, read, output, to, standalone, self_contained):
    if not filter_to:
        raise KnittyError(f"Invalid Pandoc filter arg: '{filter_to}'")

    fmts = dict(commonmark='md', markdown='md', gfm='md')
    if output and (output != '-'):
        dir_name = p.basename(output).replace('.', '_')
    elif input_file and (input_file != '-'):
        dir_name = p.basename(input_file).replace('.', '_') + '_' + fmts.get(filter_to, filter_to)
    else:
        dir_name = 'stdout' + '_' + fmts.get(filter_to, filter_to)

    pandoc_extra_args = ctx.args
    if standalone:
        pandoc_extra_args.append('--standalone')
    if self_contained:
        pandoc_extra_args.append('--self-contained')

    out = knitty_pandoc_filter(sys.stdin.read(),
                               name=dir_name,
                               filter_to=filter_to,
                               standalone=standalone,
                               self_contained=self_contained,
                               pandoc_format=read,
                               pandoc_extra_args=pandoc_extra_args)
    if filter_to == 'ipynb':
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
