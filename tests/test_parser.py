import pytest
import knitty.preprocess_filter as P
from knitty.preprocess_filter import Token


class TestParser:
    @pytest.mark.parametrize('options, expected', [
        ('python', '.python'),
        ('r, name', '.r .name'),
        ('r, echo=True', '.r echo=True'),
        ('r, name, echo=True, eval=False',
         '.r .name echo=True eval=False'),
        ('r, fig.cap="Caption"', '.r fig.cap="Caption"'),
        ('r, fig.cap="Cap, 2", echo=True',
         '.r fig.cap="Cap, 2" echo=True'),
        ('r, echo=True, fig.cap="Cap, 2"',
         '.r echo=True fig.cap="Cap, 2"'),
        ('r, fig.cap="Caption, too"', '.r fig.cap="Caption, too"'),
    ])
    def test_preprocess(self, options, expected):
        result = P.preprocess_options(options)
        assert result == expected

    def test_tokenize(self):
        line = 'r, fig.width=bar'
        result = P.tokenize(line)
        expected = [
            Token('ARG', 'r'),
            Token('DELIM', ', '),
            Token('KWARG', 'fig.width=bar'),
        ]
        assert result == expected

    def test_tokenize_quote(self):
        line = 'r, fig.cap="A, Caption", echo=True'
        result = P.tokenize(line)
        expected = [
            Token('ARG', 'r'),
            Token('DELIM', ', '),
            Token('KWARG', 'fig.cap="A, Caption"'),
            Token('DELIM', ', '),
            Token('KWARG', 'echo=True'),
        ]
        assert result == expected

    @pytest.mark.parametrize('kind,text,expected', [
        ("ARG", "r", (
            ("r",), ()
        )),
        ("DELIM", ", ", (
            (), ()
        )),
        ("KWARG", "foo=bar", (
            (), (("foo", "bar"),)
        )),
    ])
    def test_sort_args(self, kind, text, expected):
        args, kwargs = [], []
        P.sort(kind, text, args, kwargs)
        assert (tuple(args), tuple(kwargs)) == expected

    def test_sort_raises(self):
        args, kwargs = [], []
        with pytest.raises(TypeError):
            P.sort('fake', 'foo', args, kwargs)
