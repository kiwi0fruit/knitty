import sys
import panflute as pf

MATCH = 'match'


def action(elem, doc):
    if isinstance(elem, pf.CodeBlock):
        match = elem.attributes.get(MATCH, doc.get_metadata(MATCH))
        if str(match).lower() == 'true':
            elem.classes = ["{{.{}}}".format(MATCH)] + elem.classes

_help = '''pre-notedown reads from stdin and writes to stdout. Usage:

`pre-notedown TO` - run Pandoc filter that prepares code blocks for md to ipynb conversion via Notedown.
Code blocks for cells should to have `match=True` key word attribute.
Intended to be later used with:
`pandoc -f json --standalone --self-contained -t markdown-fenced_code_attributes | knotedown match=match`,

`pre-notedown --help` or `pre-notedown -h` - show this message and exit.
'''


def main(doc=None):
    if len(sys.argv) > 1:
        if sys.argv[1] == '--help' or sys.argv[1] == '-h':
            print(_help)
            return None
    return pf.run_filter(action, doc=doc)

if __name__ == '__main__':
    main()
