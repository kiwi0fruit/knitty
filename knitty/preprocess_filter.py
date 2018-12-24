"""
Some code was taken from
Chunk options-line parser
from MIT licensed Stitch by Tom Augspurger
https://github.com/pystitch/stitch
that originally comes from *Python Cookbook* 3E, recipie 2.18
"""
import re
import yaml
from collections import namedtuple
from typing import List, Tuple, Iterable

Token = namedtuple("Token", ['kind', 'value'])

# -------------------------------------------
# Python text preprocess filter
# -------------------------------------------

# -----------------------------------
# Constants
# -----------------------------------
# Grammar:
# ---------------------------------
CELL = '%%'
CHUNK = '```'
DEC = '@'
# Chunk options:
# ---------------------------------
DEFAULT_EXT = 'py'
CHUNK_NAME = 'chunk'
MARKDOWN_KERNELS = ('markdown', 'md')
# Metadata options:
# ---------------------------------
META_COMMENTS_MAP = 'comments-map'
META_KNITTY_COMMENTS_EXT = 'knitty-comments-ext'


# -----------------------------------
# Search and replace:
# -----------------------------------
class SEARCH:
    """
    Regex constants for Search and replace.

    Public:

    * KEY: Starts with alphabetic or ``_``
    * VAL: ``val``, ``"val"``, ``'val'``
    * SPACE: All whitespace characters except ``\\r`` and ``\\n``

    Private:

    * _KWARG: ``key=val``
    * _ARG: ``key`` or ``key=val``

    * _GFM_LANG: ``lang`` or ``key=val``
    * _GFM_LANG2: ``lang`` or nothing
    * _RMARK_LANG: ``lang`` or ``key=val, k=v``
        (to make them distinct from pandoc options we need at least one comma)

    * _GFM_OPT: ``lang, chunk, key=val, id=ID`` or ``key=val``
    * _RMARK_OPT: ``lang, chunk, key=val, id=ID`` or ``key=val, k=v``

    * _GFM (GitHub Flavoured Markdown): ``@{lang, chunk, key=val, id=id1}\\n```lang2`` or ``@{key=val}\\n`````
    * _RMARK (RMarkdown): ``"```{lang, chunk, key=val, id=id1}"``
    * _HYDRO_LINE (Atom Hydrogen): ``# %% {lang, chunk, key=val, id=id1} comment text``

    Public:

    1. PATTERN: compiled regex
        * Has groups: OPT, RMARK_OPT, LANG, LANG2, RMARK_LANG
        * Search pattern for Stitch-markdown doc
    2. HYDRO_FIRST_LINE: compiled regex
        * Has significant groups: COMM
        * ``# %% {lang, chunk, key=val, id=id1} comment text``
          Specifies inline comments patterns in Hydrogen documents's first line (cell blocks mode)
    3. hydro_regex: returns compiled regex
        * Has groups: OPT, LANG, BODY (later BEGIN, END, NL_POST_BEGIN, NL_PRE_END groups might be added)
        * Has format slots: comm, opt, begin, end
        * Search pattern in Hydrogen document. Block comments can be specified if they are turned on.
    """
    # Public: --------------------------------
    # language=PythonRegExp
    KEY = r'[^\W\d](?:[-.\w]*[-\w])?'  # language=PythonRegExp
    VAL = '(?:"[^"]*"|\'[^\']*\'|[^\\s,{}"\'][^\\s,{}]*)'  # language=PythonRegExp
    SPACE = r'[^\S\r\n]*'

    # Private: --------------------------------
    _ = SPACE
    _KWARG = rf'{KEY}{_}={_}{VAL}'
    _ARG = rf'{KEY}({_}={_}{VAL})?'

    _LANG = re.compile(rf'((?P<LANG>{KEY})|{{alt}})').pattern
    _GFM_LANG = _LANG.format(alt=_KWARG)
    _GFM_LANG2 = _LANG.format(alt='').replace('<LANG>', '<LANG2>')
    _RMARK_LANG = _LANG.format(alt=rf'{_KWARG}{_},{_}{_KWARG}').replace('<LANG>', '<RMARK_LANG>')

    _OPT = re.compile(rf'{{{_}(?P<OPT>{{lang}}({_},{_}{_ARG})*){_}\}}').pattern  # {{ \}} are escaped { } in regex + rf
    _GFM_OPT = _OPT.replace('{lang}', _GFM_LANG)
    _RMARK_OPT = _OPT.replace('{lang}', _RMARK_LANG).replace('<OPT>', '<RMARK_OPT>')

    _HYDRO_LINE = re.compile(rf'{{comm}} *{CELL}( +{{opt}})?( [^\r\n]*?)?(\r?\n|$)').pattern
    _RMARK = rf'{CHUNK}{_}{_RMARK_OPT}{_}'
    _GFM = re.compile(rf'{DEC}{_GFM_OPT}{_}\r?\n{CHUNK}{_}{_GFM_LANG2}{_}').pattern

    # Public: --------------------------------
    PATTERN = re.compile(rf'((\r?\n|^)({_GFM}|{_RMARK})(\r?\n|$))')
    HYDRO_FIRST_LINE = re.compile(_HYDRO_LINE.format(  # language=PythonRegExp
        comm=r'^(?P<COMM>[^\s]{1,3})',
        opt=_GFM_OPT
    ))

    @staticmethod
    def hydro_regex(comm: str, begins: Tuple[str]=None, ends: Tuple[str]=None):
        def del_named_groups(regex: str) -> str:
            return re.sub(r'\?P<\w+>', '', regex)

        def escaped_regex(it: Iterable[str], group_name: str) -> str:
            return re.compile(rf"(?P<{group_name}>{'|'.join(map(re.escape, it))})?").pattern

        _line = SEARCH._HYDRO_LINE.format(comm=comm, opt=SEARCH._GFM_OPT)  # language=PythonRegExp
        ends = (r'(?P<NL_PRE_END>\r?\n?)' + escaped_regex(ends, 'END')) if ends else ''  # language=PythonRegExp
        begins = (escaped_regex(begins, 'BEGIN') + r'(?P<NL_POST_BEGIN>\r?\n?)') if begins else ''

        return re.compile(
            rf'(((?<=\n)|^){_line}|^){begins}(?P<BODY>.*?){ends}\s*(?=\n{del_named_groups(_line)}|$)',
            re.DOTALL)


class Replacer:
    def __init__(self, lang: str=None, block_comm: Tuple[str]=()):
        """
        Sets default language. Initiates some bool vars.

        Parameters
        ----------
        lang :
            Default language via extension. Must be non-empty string,
            otherwise it would be DEFAULT_EXT (py).
        block_comm :
            ...
        """
        self._lang = lang if isinstance(lang, str) and lang else DEFAULT_EXT
        self._block_comm = block_comm

    def replace(self, m) -> str:
        """
        Replaces options in Stitch format with options in Pandoc format.
        Takes language from the following GFM code chunk if it wasn't
        provided like in ``@{key=value}``. If no language provided then
        takes default from ``self._lang``.

        Then options line is processed by ``preprocess_options()`` function.

        Note: in Stitch format `````{lang, key=val}`` the options are to be
        replaced only if they start with a name without a dot ``{lang}``
        or if they separated with a comma ``{key=val, k=v}``. Otherwise
        they are considered standard Pandoc options and are not
        replaced.

        Parameters
        ----------
        m :
            Regex match
        """
        gfm, rmark = m.group('OPT'), m.group('RMARK_OPT')
        if gfm is not None:
            opt, lang, lang2 = gfm, m.group('LANG'), m.group('LANG2')
        elif rmark is not None:
            opt, lang, lang2 = rmark, m.group('RMARK_LANG'), None
        else:
            raise TypeError("Regex bug, `else:` should never happen.")
        if lang is None:
            _lang = lang2 if (lang2 is not None) else self._lang
            opt = _lang + ', ' + opt

        return '\n```{{{opt}}}\n'.format(opt=preprocess_options(opt))

    def replace_cells(self, m) -> str:
        """
        Converts text piece starting from ``# %%`` or BOF
        and ending right before next ``# %%`` or EOF.

        Converts document with Hydrogen code cells
        (``%%`` format only) to markdown document with
        code chunks. Separators should be of the format:
        ``# %% {lang, arg, kwarg=val} something else``,
        Stitch options are optional. Instead of ``#`` there
        can be language specific inline comment symbol.
        The input document for example is a valid python file.

        Parameters
        ----------
        m :
            Regex match
        """
        def read(group_name: str):
            group = m.group(group_name)
            if group is None:
                group = ''
            return group

        body = read('BODY')
        out = body

        # deal with begin/end block comments:
        block_comm = False
        if self._block_comm:
            begin, end = read('BEGIN'), read('END')
            nl_post_begin, nl_pre_end = read('NL_POST_BEGIN'), read('NL_PRE_END')
            if (begin, end) in self._block_comm:
                if not re.search(rf"{re.escape(begin)}|{re.escape(end)}", body):
                    block_comm = True
            if not block_comm:
                if begin:
                    out = begin + nl_post_begin + out
                if end:
                    out = out + nl_pre_end + end

        # read options and fallback them:
        opt, lang = read('OPT'), read('LANG')
        lang_fallback = MARKDOWN_KERNELS[0] if block_comm else self._lang
        if opt:
            if not lang:
                lang = lang_fallback
                opt = lang + ', ' + opt
        else:
            lang = lang_fallback
            opt = lang

        # prepare output:
        if out:
            if lang in MARKDOWN_KERNELS:
                return out + '\n\n'
            else:
                return f'```{{{preprocess_options(opt)}}}\n{out}\n```\n\n'
        else:
            return ''


def knitty_preprosess(source: str, lang: str=None, yaml_meta: str=None) -> str:
    """
    Stitch options preprocess function. Transforms document.

    Also converts document with Hydrogen code cells
    to markdown document with code chunks.

    Parameters
    ----------
    source :
        ...
    lang :
        Default language. When used with `pre-knitty` CLI the file's extension is passed.
        If `lang` arg is `None` but `knitty-comments-ext` metadata key is set then uses the key.
        Otherwise uses 'py' that is `Replacer` class default.
    yaml_meta :
        pre-knitty settings via read YAML file contents
    """
    def load_yaml(string: str or None):
        if isinstance(string, str) and string:
            found = re.search(r'(?:^|\n)---\n(.+?\n)(?:---|\.\.\.)(?:\n|$)', string, re.DOTALL)
            if found:
                loaded = yaml.load(found.group(1))
                if isinstance(loaded, dict):
                    return loaded
        return None

    def get(maybe_dict, key: str):
        return maybe_dict.get(key, None) if isinstance(maybe_dict, dict) else None

    def good_str(maybe_str) -> str or None:
        """ :return: non-empty str or None """
        return maybe_str if maybe_str and isinstance(maybe_str, str) else None

    # Read metadata:
    metadata = load_yaml(source)
    # Read code language extension from metadata (overrides argument):
    comment_lang = good_str(get(metadata, META_KNITTY_COMMENTS_EXT))
    if lang and not comment_lang:
        comment_lang = lang
    elif not lang and comment_lang:
        lang = comment_lang

    def comments() -> List[str] or None:
        """ Returns comments list if found them in right format. """
        for meta in (lambda: metadata, lambda: load_yaml(yaml_meta)):
            comments_map = get(meta(), META_COMMENTS_MAP)
            _comments = get(comments_map, comment_lang)
            if isinstance(_comments, list):
                if len(_comments) % 2 == 1:
                    if all(isinstance(s, str) and s for s in _comments):
                        return _comments
        return None

    comments = comments()
    first_line = SEARCH.HYDRO_FIRST_LINE.match(source)
    if comments or first_line:
        block_comm = tuple()
        if comments:
            comm = re.escape(comments[0])
            if len(comments) > 2:
                block_comm = tuple((comments[i], comments[i + 1])
                                   for i in range(1, len(comments), 2))
        else:
            comm = re.escape(first_line.group('COMM'))

        source = re.sub(SEARCH.hydro_regex(comm=comm,
                                           begins=tuple(str(begin) for begin, e in block_comm),
                                           ends=tuple(str(end) for b, end in block_comm)),
                        Replacer(lang, block_comm).replace_cells,
                        source + '\n')  # regex assumes new line at the end

    return re.sub(SEARCH.PATTERN, Replacer(lang).replace, source)


# -----------------------------------
# Transform options to Pandoc format:
# -----------------------------------
class OPT:
    """
    Regex constants for validating and parsing options.

    * _ARG: str
        ``key``
    * _DELIM: str
        ``,``
    * KWARG: str
        ``key=val``, ``key="val"``, ``key='val'``
    * PATTERN: compiled regex
        KWARG or _ARG or _DELIM
        Pattern with valid tokens
    * NAME: compiled regex
        ``^key$`` where ``^``/``$`` mark begin/end of the string
    """
    KEY, _ = SEARCH.KEY, SEARCH.SPACE  # language=PythonRegExp
    _ARG = rf'(?P<ARG>{KEY})'  # language=PythonRegExp
    _DELIM = rf'(?P<DELIM>{_},{_})'  # language=PythonRegExp
    KWARG = rf'(?P<KWARG>(?P<KEY>{KEY}){_}={_}(?P<VAL>{SEARCH.VAL}))'

    PATTERN = re.compile('|'.join([KWARG, _ARG, _DELIM]))
    NAME = re.compile(rf'^{KEY}$')


def tokenize(options_line: str) -> List[Token]:
    """
    Break an options line into a list of tokens.

    Returns
    -------
    tokens :
        list of named tuples
    """
    def generate_tokens(pat, text):
        scanner = pat.scanner(text)
        for m in iter(scanner.match, None):
            yield Token(m.lastgroup, m.group(m.lastgroup))

    # noinspection PyTypeChecker
    tok = list(generate_tokens(OPT.PATTERN, options_line))
    return tok


def check_and_change(args: List[str],
                     kwargs: List[Tuple[str, str]]
                     ) -> Tuple[List[str], List[Tuple[str, str]]]:
    """
    Transform args and kwargs.

    * Checks classes names
    * Checks values format of keys:
      ``id``,
      ``class``,
      ``chunk``
    * Sets chunk value the second positional argument

    Parameters
    ----------
    args :
        ...
    kwargs :
        [(key, val), ...]

    Return
    ------
    tuple :
        (args, kwargs)
    """
    chunk = None

    def check(kwarg):
        key, val = kwarg
        nonlocal args, chunk
        if key == CHUNK_NAME and chunk is None:
            chunk = val
        elif key == 'class':
            n = len(val)
            val = val.strip('"')
            if n == len(val):
                val = val.strip("'")
            args += val.split()
        elif key == 'id':
            if OPT.NAME.match(val):
                return True
            else:
                raise TypeError("Invalid id name: " + val)
        else:
            return True
        return False

    kwargs = [kwarg for kwarg in kwargs if check(kwarg)]
    # move `chunk` option:
    if chunk is not None:
        args = [args[0], chunk] + args[1:]
    # check classes names:
    for arg in args:
        if not OPT.NAME.match(arg):
            raise TypeError("Invalid class name: " + arg)

    return args, kwargs


def preprocess_options(options_line: str) -> str:
    """
    Transform a code-chunk options line to allow\n
    ``lang, chunk, key=val, id = ID`` instead of pandoc-style\n
    ``.lang .chunk key=val id=ID`` (also removes extra whitespaces).
    """
    args, kwargs = [], []

    def sort(kind, text) -> str or None:
        if kind == 'ARG':
            args.append(text)
        elif kind == 'DELIM':
            pass
        elif kind == 'KWARG':
            m = re.match(OPT.KWARG, text)
            kwargs.append((m.group('KEY'), m.group('VAL')))
        else:
            raise TypeError('Unknown kind %s' % kind)

    for kind_, text_ in tokenize(options_line):
        sort(kind_, text_)
    args, kwargs = check_and_change(args, kwargs)

    return ' '.join(['.' + arg for arg in args] + [key + '=' + val for key, val in kwargs])
