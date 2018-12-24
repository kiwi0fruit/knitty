"""
Alternative CLI for
knotedown --match=in --nomagic
that reads from stdin and writes to stdout
('in' should now be set in metadata).
"""
import sys
from .consts import META_CODECELL_MATCH
from .tools import load_yaml
from .notedown.notedown import MarkdownReader


def main(text: str) -> str:
    """
    Converts Markdown document with specially marked code cells to ipynb
    (together with global yaml metadata section that should be right at the start of the doc).
    A text filter that reads from stdin and writes to stdout. Can use metadata option:
    `codecell-match-class: in` (default value is `in`) that is a Pandoc class that marks Jupyter code cells.
    If `codecell-match-class: ''` (empty string) then all Markdown code cells would be
    converted to Jupyter code cells.
    """
    metadata = load_yaml(text)[1]
    return text


def cli():
    if len(sys.argv) > 1:
        if sys.argv[1].lower() == '--help':
            print(main.__doc__)
            return
    sys.stdout.write(main(sys.stdin.read()))


if __name__ == '__main__':
    cli()
