"""
CLI wrapper for stitch_preprosess function
"""
import sys
from os import path as p
from .preprocess_filter import knitty_preprosess
import click
from .consts import META_COMMENTS_MAP, META_KNITTY_COMMENTS_EXT, META_KNITTY_LANG


@click.command(help=f"""A text filter that reads from stdin and writes to stdout.
INPUT_FILE is optional but it helps to determine language and hence a Jupyter kernel.\n
Settings that can be set in stdin OR in the --yaml file:\n
---\n
{META_COMMENTS_MAP}:\n
  py: ['#', "'''", "'''", "\\\"\\\"\\\"", "\\\"\\\"\\\""]\n
  js: ["//", "/*", "*/"]\n
...\n
Can be set in stdin metadata only: 1) Force set document default language name,
2) extenstion to get from `{META_COMMENTS_MAP}`:\n
---\n
{META_KNITTY_LANG}: 'py2'\n
{META_KNITTY_COMMENTS_EXT}: 'py'\n
...\n
""")
@click.argument('input_file', type=click.Path(), default=None, required=False)
@click.option('-y', '--yaml', 'yaml_meta', type=click.Path(), default=None, required=False,
              help='yaml metadata file (wrapped in ---... like in pandoc) with settings for pre-knitty. ')
def main(input_file, yaml_meta):
    ext = p.splitext(p.basename(input_file))[1].lstrip('.') if input_file else None
    if yaml_meta:
        with open(yaml_meta, 'r', encoding='utf-8') as y:
            yaml_meta = y.read()
    sys.stdout.write(knitty_preprosess(sys.stdin.read(), ext, yaml_meta))


if __name__ == '__main__':
    main()
