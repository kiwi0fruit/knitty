import sys
from .ast_filter import knitty_pandoc_filter
import click
import os
import re
import panflute as pf
import io


def action(elem, doc):
    if isinstance(elem, pf.CodeBlock):
        input_ = elem.attributes.get('input', doc.get_metadata('input'))
        if str(input_).lower() == 'true':
            match = str(doc.get_metadata('match', 'in'))
            if match not in elem.classes:
                elem.classes.append(match)
            id_ = elem.identifier
            id_ = ("#" + id_ + " ") if (id_ != "" and id_ is not None) else ""
            classes = " .".join(elem.classes)
            classes = ("." + classes + " ") if (classes != "") else ""
            kwargs = " ".join(["{}={}".format(k, v) for k, v in elem.attributes.items()])
            elem.classes[0] = "{" + id_ + classes + kwargs + "}"


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
        raise Exception('Invalid -t/-w/--to/--write option: {}'.format(to))


@click.command(
    context_settings=dict(ignore_unknown_options=True,
                          allow_extra_args=True),
    help="Knitty is a Pandoc filter with arguments. It reads from stdin and writes to stdout." +
    "INPUT_FILE is optional but it helps to auto-name Knitty data folder in some cases."
)
@click.pass_context
@click.argument('input_file', type=str, default=None, required=False)
@click.option('-f', '-r', '--from', '--read', type=str, default="markdown",
              help='Pandoc reader option. Specify input format.')
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
@click.option('--to-ipynb', is_flag=True, default=False,
              help='Additionally run Pandoc filter that prepares code blocks for md to ipynb conversion via Notedown.')
def main(ctx, input_file, read, output, to, standalone, self_contained, dir_name, to_ipynb):
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
    
    pandoc_extra_args = ctx.args
    if standalone:
        pandoc_extra_args.append('--standalone')
    if self_contained:
        pandoc_extra_args.append('--self-contained')
    # Knitty (Stitch) later do not need `to` in `pandoc_extra_args` so loosing it is OK
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
