import sys
import panflute as pf


def action(elem, doc):
    if isinstance(elem, pf.CodeBlock):
        input = elem.attributes.get('input', doc.get_metadata('input'))
        if str(input).lower() == 'true':
            match = str(doc.get_metadata('match', 'in'))
            if match not in elem.classes:
                elem.classes.append(match)
            id_ = elem.identifier
            id_ = ("#" + id_ + " ") if (id_ != "" and id_ is not None) else ""
            classes = " .".join(elem.classes)
            classes = ("." + classes + " ") if (classes != "") else ""
            kwargs = " ".join(["{}={}".format(k, v) for k, v in elem.attributes.items()])
            elem.classes[0] = "{" + id_ + classes + kwargs + "}"

_help = '''pre-notedown reads from stdin and writes to stdout. Usage:

`pre-notedown TO` - run Pandoc filter that prepares code blocks for md to ipynb conversion via Notedown.
Code blocks for cells should have `input=True` key word attribute (default `input` value can set in metadata section).
Intended to be later used with:
`pandoc -f json --standalone --self-contained -t markdown-fenced_code_attributes | knotedown --match=in`,
Other match value can be set in metadata section like `match: in`.

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
