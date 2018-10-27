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
from typing import List, Iterable

# -------------------------------------------
# Python text preprocess filter
# -------------------------------------------

# -----------------------------------
# Constants
# -----------------------------------
Token = namedtuple("Token", ['kind', 'value'])
# Grammar:
# ---------------------------------
CELL = '%%'
BLOCK_COMM_DEF = '%%%'
CHUNK = '```'
DEC = '@'
# Chunk options:
# ---------------------------------
DEFAULT_EXT = 'py'
CHUNK_NAME = 'chunk'
MARKDOWN_KERNELS = ('md', 'markdown')
META_COMMENTS_MAP = 'comments-map'
META_KNITTY = 'knitty'
META_KNITTY_COMMENTS = 'comments'
META_KNITTY_LANGUAGE = 'language'

# Regexps:
# ---------------------------------
# KEY: Starts with alphabetic or `_`
# VAL: `val`, `"val"`, `'val'`
# SPACE: All whitespace characters except `\r` and `\n`
#                                    language=PythonRegExp
KEY = r'[^\W\d](?:[-.\w]*[-\w])?'  # language=PythonRegExp
VAL = '(?:"[^"]*"|\'[^\']*\'|[^\\s,{}"\'][^\\s,{}]*)'  # language=PythonRegExp
SPACE = r'[^\S\r\n]*'


# -----------------------------------
# Search and replace:
# -----------------------------------
class SEARCH:
    """
    Regex constants for Search and replace.

    Private:
    --------
    _KWARG: `key=val`
    _ARG: `key` or `key=val`

    _GFM_LANG: `lang` or `key=val`
    _GFM_LANG2: `lang` or nothing
    _RMARK_LANG: `lang` or `key=val, k=v`

    _GFM_OPT: `lang, chunk, key=val, id=ID` or `key=val`
    _RMARK_OPT: `lang, chunk, key=val, id=ID` or `key=val, k=v`

    _GFM (GitHub Flavoured Markdown): "@{lang, chunk, key=val, id=id1}\n```lang2" or "@{key=val}\n```"
    _RMARK (RMarkdown): "```{lang, chunk, key=val, id=id1}"
    _HYDRO_LINE (Atom Hydrogen): "# %% {lang, chunk, key=val, id=id1} comment text"

    Public:
    -------
    PATTERN: compiled regex
        * Has groups: OPT, RMARK_OPT, LANG, LANG2, RMARK_LANG
        * Search pattern for Stitch-markdown doc
    HYDRO_FIRST_LINE: compiled regex
        * Has groups: COMM
        * "# %% {lang, chunk, key=val, id=id1} comment text"
          Specifies inline comments patterns in Hydrogen documents's first line (cell blocks mode)
    HYDRO: str
        * Has groups: FIRST, LAST, LANG (later BEGIN, END groups should be added)
        * Has `.format()` slots: comm, opt, begin, end
        * Search pattern in Hydrogen document. Block comments can be specified if turned on.
    OPT: str
        * Has groups: OPT
        * Doesn't have `.format()` slots
        * Same as _GFM_OPT
    """
    _ = SPACE
    _KWARG = rf'{KEY}{_}={_}{VAL}'  # language=PythonRegExp
    _ARG = rf'{KEY}({_}={_}{VAL})?'  # language=PythonRegExp

    _LANG = rf'((?P<LANG>{KEY})|{{alt}})'
    _GFM_LANG = _LANG.format(alt=_KWARG)
    _GFM_LANG2 = _LANG.format(alt='').replace('<LANG>', '<LANG2>')
    _RMARK_LANG = _LANG.format(alt=rf'{_KWARG}{_},{_}{_KWARG}').replace('<LANG>', '<RMARK_LANG>')
    #   language=PythonRegExp
    _OPT = rf'{{{_}(?P<OPT>{{lang}}({_},{_}{_ARG})*){_}\}}'
    # Note: {{ \{{ \}} are escaped { } in regex + rf""
    _GFM_OPT = _OPT.replace('{lang}', _GFM_LANG)
    _RMARK_OPT = _OPT.replace('{lang}', _RMARK_LANG).replace('<OPT>', '<RMARK_OPT>')  # language=PythonRegExp

    _HYDRO_LINE = rf'{{comm}} *{CELL}( +{{opt}})?( .*)?\r?\n'
    _RMARK = rf'{CHUNK}{_}{_RMARK_OPT}{_}'  # language=PythonRegExp
    _GFM = rf'{DEC}{_GFM_OPT}{_}\r?\n{CHUNK}{_}{_GFM_LANG2}{_}'

    # Public attributes:
    # ------------------
    PATTERN = re.compile(rf'((\r?\n|^)({_GFM}|{_RMARK})(\r?\n|$))')  # language=PythonRegExp
    HYDRO = r'((?P<FIRST>^)|{{end}}\r?\n)\s*((?P<LAST>$)|{line}{{begin}})'.format(
        line=_HYDRO_LINE.format(comm='{comm}', opt=rf'{{{_GFM_OPT}}}')
    )  # TODO I moved {end} and removed \n so behaviour changed
    HYDRO_FIRST_LINE = re.compile(_HYDRO_LINE.format(  # language=PythonRegExp
        comm=r'^(?P<COMM>[^\s]{1,3})',
        opt=_GFM_OPT
    ))


class Replacer:
    def __init__(self, lang: str=None, block_comm: any=False):
        """
        Sets default language. Initiates some bool vars.
        :param lang: str
            Default language. Must be string of positive length,
            otherwise it would be DEFAULT_EXT.
        :param block_comm: any
            Would be converted to bool.
        """
        self._lang = lang if isinstance(lang, str) and lang else DEFAULT_EXT
        self._use_block_comm = bool(block_comm)
        self._opened_block_comm = False
        self._prev_was_md = False

    def replace(self, m) -> str:
        """
        Replaces options in Stitch format with options in Pandoc format.
        Takes language from the following GFM code chunk if it wasn't
        provided like in `@{key=value}`. If no language provided then
        takes default from `self._lang`.

        Then options line is processed by `preprocess_options()` function.

        Note: in Stitch format ```{lang, key=val} the options are to be
        replaced only if they start with a name without a dot `{lang}`
        or if they separated with a comma `{key=val, k=v}`. Otherwise
        they are considered standard Pandoc options and are not
        replaced.

        :param m:
            Regex match
        :return: str
            New string
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
        Converts document with Hydrogen code cells
        (`%%` format only) to markdown document with
        code chunks. Separators should be of the format:
        `# %% {lang, arg, kwarg=val} something else`,
        Stitch options are optional. Instead of `#` there
        can be language specific inline comment symbol.
        The input document for example is a valid python file.

        :param m:
            Regex match
        :return: str
            New string
        """
        # print(lang, cells_mode, file=open(r'D:\debug.txt', 'w', encoding='utf-8'))  # TODO
        # read options and fix them:
        opt, lang = m.group('OPT'), m.group('LANG')
        if opt is not None:
            if lang is None:
                lang = self._lang
                opt = lang + ', ' + opt
        else:
            lang = self._lang
            opt = lang

        # prepare output pattern:
        pre, post = '', ''
        first, last = (m.group('FIRST') is not None), (m.group('LAST') is not None)
        #    add the closing block comment to the end of the code
        #    if opening block comment wasn't removed:
        if self._use_block_comm:
            begin, end = m.group('BEGIN'), m.group('END')
            if (end is not None) and (end != '') and (not self._opened_block_comm):
                pre += end
            if (begin is not None) and (begin != ''):
                self._opened_block_comm = True
            else:
                self._opened_block_comm = False

        #    process previous code chunk:
        if not first:
            pre += '\n'
            if self._prev_was_md:
                pre += '\n'
            else:
                pre += '```\n\n'

        #    process next code chunk:
        if not last:
            if lang in MARKDOWN_KERNELS:
                post += '\n'
                self._prev_was_md = True
            else:
                post += '```{{{opt}}}\n'
                self._prev_was_md = False

        # process output pattern:
        return (pre + post).format(opt=preprocess_options(opt))


def knitty_preprosess(source: str, lang: str=None, yaml_meta: str=None) -> str:
    """
    Stitch options preprocess function.

    Also converts document with Hydrogen code cells
    to markdown document with code chunks.

    :param source: str
    :param lang: str
        Default language
    :param yaml_meta: str
        pre-knitty settings
    :return: str
        New source
    """
    def load_yaml(string):
        m = re.search(r'(?:^|\n)---\n(.+?\n)(?:---|\.\.\.)(?:\n|$)', string, re.DOTALL)
        return yaml.load(m.group(1)) if m else None

    def get(maybe_dict, key: str):
        return maybe_dict.get(key, None) if isinstance(maybe_dict, dict) else None
    # Read metadata:
    _knitty = get(load_yaml(source), META_KNITTY)
    # Read code language:
    _lang = get(_knitty, META_KNITTY_LANGUAGE)
    lang = _lang if _lang and isinstance(_lang, str) else lang

    def _comments() -> List[str] or None:
        """Returns comments list if found them in right format."""
        comments = get(_knitty, META_KNITTY_COMMENTS)
        if isinstance(comments, list):
            if len(comments) % 2 == 1:
                if all(isinstance(s, str) and s for s in comments):
                    return comments
        comments_map = get(load_yaml(yaml_meta), META_COMMENTS_MAP)
        comments = get(comments_map, lang)
        if isinstance(comments, list):
            if len(comments) % 2 == 1:
                if all(isinstance(s, str) and s for s in comments):
                    return comments
        return None

    cells_mode = _comments()
    cells_mode = SEARCH.HYDRO_FIRST_LINE.match(source) if not cells_mode else cells_mode
    if cells_mode:
        block_comm = None
        if isinstance(cells_mode, list):
            comm = cells_mode[0]
            if len(cells_mode) > 1:
                block_comm = [(cells_mode[i], cells_mode[i + 1])
                              for i in range(1, len(cells_mode), 2)]
        else:
            comm = re.escape(cells_mode.group('COMM'))

        begin, end = '', ''
        if block_comm:
            def escaped_regex(it: Iterable[str], group_name: str):
                return rf"(?P<{group_name}>{'|'.join(map(re.escape, it))})?"
            begin = escaped_regex((begin for begin, e in block_comm), 'BEGIN')
            end = escaped_regex((end for b, end in block_comm), 'END')

        source = re.sub(SEARCH.HYDRO.format(comm=comm, begin=begin, end=end),
                        Replacer(lang, block_comm).replace_cells,
                        source + '\n')  # regex assumes new line at the end

    return re.sub(SEARCH.PATTERN, Replacer(lang).replace, source)


# -----------------------------------
# Transform options to Pandoc format:
# -----------------------------------
class OPT:
    """
    Regex constants for validating and parsing options.

    _ARG: str
        `key`
    _DELIM: str
        `,`
    KWARG: str
        `key=val`, `key="val"`, `key='val'`
    PATTERN: compiled regex
        KWARG or _ARG or _DELIM
        Pattern with valid tokens
    NAME: compiled regex
        `^key$` where ^/$ mark begin/end of the string
    """
    _ = SPACE  # language=PythonRegExp
    _ARG = rf'(?P<ARG>{KEY})'  # language=PythonRegExp
    _DELIM = rf'(?P<DELIM>{_},{_})'  # language=PythonRegExp
    KWARG = rf'(?P<KWARG>(?P<KEY>{KEY}){_}={_}(?P<VAL>{VAL}))'

    PATTERN = re.compile('|'.join([KWARG, _ARG, _DELIM]))
    NAME = re.compile(rf'^{KEY}$')


def tokenize(options_line):
    """
    Break an options line into a list of tokens.

    Parameters
    ----------
    options_line : str

    Returns
    -------
    tokens : list of tuples
    """
    def generate_tokens(pat, text):
        scanner = pat.scanner(text)
        for m in iter(scanner.match, None):
            yield Token(m.lastgroup, m.group(m.lastgroup))

    # noinspection PyTypeChecker
    tok = list(generate_tokens(OPT.PATTERN, options_line))
    return tok


def check_and_change(args, kwargs):
    """
    * Adds `eval=True` if `eval` was not specified
    * Checks classes names
    * Checks values format of keys:
      `id`
      `class`
      `chunk`
    * Sets chunk value the second positional argument

    Parameters
    ----------
    args: list of str
    kwargs: list of tuples (key: str, val: str)

    Returns
    -------
    transformed: args, kwargs
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


def preprocess_options(options_line):
    """
    Transform a code-chunk options line to allow
    `lang, chunk, key=val, id = ID` instead of pandoc-style
    `.lang .chunk key=val id=ID` (also removes extra whitespaces).

    Parameters
    ----------
    options_line: str

    Returns
    -------
    transformed: str
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
