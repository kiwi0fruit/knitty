import sys
from .ast_filter import knitty_pandoc_filter
import click
import os
import os.path as p
import re
import panflute as pf
import io
from .consts import META_CODECELL_MATCH_CLASS, DEFAULT_CODECELL_MATCH_CLASS


class KnittyError(Exception):
    pass


def action(elem, doc):
    if isinstance(elem, pf.CodeBlock):
        input_ = elem.attributes.get('input', doc.get_metadata('input'))
        if str(input_).lower() == 'true':
            match = str(doc.get_metadata(META_CODECELL_MATCH_CLASS, DEFAULT_CODECELL_MATCH_CLASS))
            if match not in elem.classes:
                elem.classes.append(match)
            id_ = elem.identifier
            id_ = ("#" + id_ + " ") if (id_ != "" and id_ is not None) else ""
            classes = " .".join(elem.classes)
            classes = ("." + classes + " ") if (classes != "") else ""
            kwargs = " ".join([f"{k}={v}" for k, v in elem.attributes.items()])
            elem.classes[0] = "{" + id_ + classes + kwargs + "}"


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
          "INPUT_FILE is optional but it helps to auto-name Knitty data folder in some cases.")
)
@click.pass_context
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
@click.option('--to-ipynb', is_flag=True, default=False,
              help=('Additionally run Pandoc filter that prepares code blocks for md to ipynb conversion via Notedown. '
                    'Code blocks for cells should have `input=True` key word attribute. Default value can be set in '
                    'metadata section like `input: True`. Intended to be later used with `knotedown --match=in`. '
                    'Another match value for knotedown can be set in metadata section like `codecell-match-class: in`.')
              )
def main(ctx, input_file, read, output, to, standalone, self_contained, dir_name, to_ipynb):
    if os.name == 'nt':
        cwd = os.getcwd()
        def cwd_pdc(ext_): return p.isfile(p.join(cwd, f'pandoc.{ext_}'))
        if cwd_pdc('exe') or cwd_pdc('cmd') or cwd_pdc('bat'):
            if cwd not in os.getenv('PATH', '').split(os.pathsep):
                raise KnittyError('Error: On Windows Pandoc is in the CWD and the CWD is not in the $PATH')

    if dir_name is None:
        if output is not None:
            dir_name = hyphenized_basename(output)
        elif input_file is not None:
            dir_name = hyphenized_basename(input_file) + '-' + dir_ext(to)
        else:
            dir_name = 'stdout-' + dir_ext(to)

    if to is not None:
        # TODO Knitty (Stitch) later checks if `to` is in ('latex', 'pdf', 'beamer') so using `dir_ext` is OK
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
    # TODO Knitty (Stitch) later do not need `to` in `pandoc_extra_args` so loosing it is OK
    out = knitty_pandoc_filter(sys.stdin.read(), name=dir_name, to=to, standalone=standalone,
                               self_contained=self_contained, pandoc_format=read,
                               pandoc_extra_args=pandoc_extra_args)
    if to_ipynb:
        with io.StringIO(out) as f:
            doc = pf.load(f)
        pf.run_filter(action, doc=doc)
        with io.StringIO() as f:
            pf.dump(doc, f)
            out = f.getvalue()
    sys.stdout.write(out)


if __name__ == '__main__':
    main()
