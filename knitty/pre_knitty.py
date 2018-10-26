"""
CLI wrapper for stitch_preprosess function:
(source: str, lang: str=None) -> str
First argument is optional file extension.
"""
import sys
from os import path as p
from .preprocess_filter import knitty_preprosess
import click



help_str = """A text filter that reads from stdin and writes to stdout.
INPUT_FILE is optional but it helps to determine language and hence a Jupyter kernel.\n
Some settings can be set in document metadata:\n
---\n
comments-map:\n
  py: ['#', {}]\n
  js: ["//", "/*", "*/"]\n
...\n
""".format(r""""\'\'\'", "\'\'\'", '\"\"\"', '\"\"\"'""")


@click.command(help=help_str)
@click.argument('input_file', type=click.Path(), default=None, required=False)
@click.option('-y', '--yaml', 'yaml_file', type=click.Path(), default=None, required=False,
                help='yaml file with settings for pre-knitty. ')
def main(input_file, yaml_file):
    ext, yaml_string = None, None
    if input_file:
        ext = p.splitext(p.basename(input_file))[1].lstrip('.')
    if yaml_file:
        with open(yaml_file, 'r', encoding='utf-8') as y:
            yaml_string = y.read()
    sys.stdout.write(knitty_preprosess(sys.stdin.read(), ext, yaml_string))


if __name__ == '__main__':
    main()
