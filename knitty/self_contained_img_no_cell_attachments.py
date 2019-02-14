import panflute as pf
from .tools import where
pf.tools.which = where  # patch panflute


# noinspection PyUnusedLocal
def action(elem, doc):
    if isinstance(elem, pf.Image):
        raw_html = re.search(
            r'<figure>.*?</figure>|<img.*?>',
            pf.convert_text(pf.Para(elem), input_format='panflute',
                            output_format='html', standalone=True,
                            extra_args=['--self-contained']),
            re.DOTALL
        ).group(0).replace('\n', '').replace('\r', '')
        return pf.RawInline(raw_html, format='html')


def main(doc=None):
    return pf.run_filter(action, doc=doc)


if __name__ == '__main__':
    main()
