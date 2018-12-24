"""
Alternative CLI for
knotedown --match=in --nomagic
that reads from stdin and writes to stdout
('in' should now be set in metadata).
"""
import sys
from .consts import META_CODECELL_MATCH_CLASS, DEFAULT_CODECELL_MATCH_CLASS
from .tools import load_yaml, get
from .notedown.notedown import MarkdownReader
import nbformat
import re


def main(text: str) -> str:
    """
    Converts Markdown document with specially marked code cells to ipynb
    (together with global yaml metadata section). A text filter that reads
    from stdin and writes to stdout.

    Can use metadata option: `codecell-match-class: in` (default value is `in`)
    that is a Pandoc class that marks Jupyter code cells.
    If `codecell-match-class: ''` (empty string) then all Markdown code cells
    would be converted to Jupyter code cells.
    """
    metadata = load_yaml(text)[1]
    match = get(metadata, META_CODECELL_MATCH_CLASS)
    if not isinstance(match, str):
        match = DEFAULT_CODECELL_MATCH_CLASS
    elif match == '':
        match = 'all'
    elif not re.match(r'^[^\W\d](?:[-.\w]*[-\w])?$', match):
        match = DEFAULT_CODECELL_MATCH_CLASS

    reader = MarkdownReader(magic=False, match=match)
    notebook = reader.reads(text)
    return nbformat.writes(notebook)


def cli():
    def stdio(): sys.stdout.write(main(sys.stdin.read()))

    if len(sys.argv) > 1:
        if sys.argv[1].lower() == '--help':
            print(main.__doc__)
        elif sys.argv[1] == '--to-ipynb':
            stdio()
        else:
            raise ValueError(f'Invalid CLI arg: {sys.argv[1]}')
    else:
        stdio()


if __name__ == '__main__':
    cli()
