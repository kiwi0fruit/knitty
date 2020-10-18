from knitty.api import knitty_preprosess
import json
import panflute as pf

import pytest
from textwrap import dedent
from knitty.stitch import Stitch

if hasattr(pf.tools, 'which'):
    from shutilwhich_cwdpatch import which
    pf.tools.which = which
else:
    from knitty.tools import KnittyError
    raise KnittyError('panflute patch failed')


def pre_stitch_ast(source: str) -> dict:
        return json.loads(pf.convert_text(knitty_preprosess(source),
                                          input_format='markdown',
                                          output_format='json'))


@pytest.fixture
def doc_meta():
    data = {'date': '2016-01-01', 'title': 'My Title', 'author': 'Jack',
            'self_contained': True, 'standalone': False}
    doc = dedent('''\
    ---
    title: {title}
    author: {author}
    date: {date}
    self_contained: {self_contained}
    standalone: {standalone}
    ---

    # Hi
    ''')
    return doc.format(**data), data


class TestOptions:

    def test_defaults(self):
        s = Stitch('', 'html')
        assert s.warning
        assert s.error == 'continue'
        assert s.standalone

    def test_override(self):
        doc = dedent('''\
        ---
        title: My Title
        standalone: False
        warning: False
        error: raise
        abstract: |
          This is the abstract.

          It consists of two paragraphs.
        ---

        # Hail and well met
        ''')
        s = Stitch('', 'html')
        s.stitch_ast(pre_stitch_ast(doc))

        assert s.standalone is False
        assert s.warning is False
        assert s.error == 'raise'
        assert getattr(s, 'abstract', None) is None

    @pytest.mark.parametrize('key', [
        'title', 'author', 'date', 'self_contained', 'standalone'
    ])
    def test_meta(self, key, doc_meta):
        doc, meta = doc_meta
        s = Stitch('', 'html')
        s.stitch_ast(pre_stitch_ast(doc))
        result = getattr(s, key)
        expected = meta[key]
        assert result == expected


class TestOptionsKernel:

    def test_fig_cap(self):
        code = dedent('''\
        ```{python, fig.cap="This is a caption"}
        import matplotlib.pyplot as plt
        plt.plot(range(4), range(4))
        ```''')
        s = Stitch('', 'html')
        result = s.stitch_ast(pre_stitch_ast(code))
        blocks = result['blocks']
        result = blocks[-1]['c'][0]['c'][1][0]['c']
        assert result == 'This is a caption'
