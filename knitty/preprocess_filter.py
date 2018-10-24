"""
Some code was taken from
Chunk options-line parser
from MIT licensed Stitch by Tom Augspurger
https://github.com/pystitch/stitch
that originally comes from *Python Cookbook* 3E, recipie 2.18
"""
import re
from collections import namedtuple


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
MARKDOWN_KERNEL = 'md'

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
        * Has groups: COMM, BEGIN, END
        * "# %% {lang, chunk, key=val, id=id1} ''' %%% ''' comment text"
          Specifies inline and block comments patterns in Hydrogen doc's first line (cell blocks mode)
    HYDRO_BLOCK_COMM: str
        * Has groups: CODE, FIRST, LAST, BEGIN, END, LANG
        * Has `.format()` slots: comm, opt, begin, end
        * Search pattern in Hydrogen doc when block comments were specified in the first line
    HYDRO: str
        * Has groups: CODE, FIRST, LAST, LANG
        * Has `.format()` slots: comm, opt
        * Search pattern in Hydrogen doc when block comments were **not** specified in the first line
    OPT: str
        * Has groups: OPT
        * Doesn't have `.format()` slots
        * Same as _GFM_OPT
    """
    #                            language=PythonRegExp
    _KWARG = r'{key}{_}={_}{val}'.format(key=KEY, val=VAL, _=SPACE)  # language=PythonRegExp
    _ARG = r'{key}({_}={_}{val})?'.format(key=KEY, val=VAL, _=SPACE)  # language=PythonRegExp

    _LANG = r'((?P<LANG>{key})|{alt})'.format(key=KEY, val=VAL, alt='{alt}', _=SPACE)  # language=PythonRegExp
    _GFM_LANG = _LANG.replace('{alt}', _KWARG)  # language=PythonRegExp
    _GFM_LANG2 = _LANG.replace('{alt}', '').replace('<LANG>', '<LANG2>')  # language=PythonRegExp
    _RMARK_LANG = _LANG.replace('<LANG>', '<RMARK_LANG>').replace(
                                '{alt}', '{kwarg}{_},{_}{kwarg}'.format(kwarg=_KWARG, _=SPACE))  # language=PythonRegExp

    _OPT = r'{{{_}(?P<OPT>{lang}({_},{_}{arg})*){_}\}}'.format(lang='{lang}', arg=_ARG, _=SPACE)
    # language=PythonRegExp    ##    Note: {{ \{{ \}} are escaped { } in regex + .format()
    _GFM_OPT = _OPT.replace('{lang}', _GFM_LANG)  # language=PythonRegExp
    _RMARK_OPT = _OPT.replace('{lang}', _RMARK_LANG).replace('<OPT>', '<RMARK_OPT>')  # language=PythonRegExp

    _HYDRO_LINE = (
        r'{comm} *{cell}( {opt})?{block_def}( .*)?\r?\n').format(cell=CELL, opt='{opt}', block_def='{block_def}',
                                                                comm='{comm}')  # language=PythonRegExp
    _RMARK = r'{chunk}{_}{opt}{_}'.format(chunk=CHUNK, _=SPACE, opt=_RMARK_OPT)  # language=PythonRegExp
    _GFM = r'{dec}{opt}{_}\r?\n{chunk}{_}{lang2}{_}'.format(dec=DEC, chunk=CHUNK, opt=_GFM_OPT, lang2=_GFM_LANG2,
                                                            _=SPACE)  # language=PythonRegExp
    _HYDRO = r'((?P<FIRST>^)|\r?\n){end}\s*((?P<LAST>$)|{line}{begin})'.format(
        line=_HYDRO_LINE.format(comm='{comm}', opt='{opt}', block_def=''),
        begin='{begin}', end='{end}'
    )
    # Public attributes:
    # ------------------
    PATTERN = re.compile(r'((\r?\n|^)({GFM}|{RMark})(\r?\n|$))'.format(GFM=_GFM, RMark=_RMARK))
    HYDRO = _HYDRO.format(begin='', end='', comm='{comm}', opt='{opt}')  # language=PythonRegExp
    HYDRO_BLOCK_COMM = _HYDRO.format(
        begin=r'(?P<BEGIN>{begin}\r?\n)?',
        end=r'(?P<END>{end}\r?\n)?',
        comm='{comm}', opt='{opt}'
    )  # language=PythonRegExp
    HYDRO_FIRST_LINE = re.compile(_HYDRO_LINE.format(
        comm=r'^(?P<COMM>[^\s]{1,3})',
        opt=_GFM_OPT,
        block_def=r'( (?P<BEGIN>[^\s]{{1,6}}) {} (?P<END>[^\s]{{1,6}}))?'.format(BLOCK_COMM_DEF)
    ))
    OPT = _GFM_OPT


class Replacer:
    def __init__(self, lang: str=None):
        """
        Sets default language. Initiates some bool vars.
        :param lang: str
            Default language. Must be string of positive length,
            otherwise it would be DEFAULT_EXT.
        """
        self._lang = lang if isinstance(lang, str) and lang != '' else DEFAULT_EXT
        self.use_block_comm = False
        self.opened_block_comm = False
        self.prev_was_md = False

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
        if self.use_block_comm:
            begin, end = m.group('BEGIN'), m.group('END')
            if (end is not None) and (end != '') and (not self.opened_block_comm):
                pre += end
            if (begin is not None) and (begin != ''):
                self.opened_block_comm = True
            else:
                self.opened_block_comm = False

        #    process previous code chunk:
        if not first:
            pre += '\n'
            if self.prev_was_md:
                pre += '\n'
            else:
                pre += '```\n\n'

        #    process next code chunk:
        if not last:
            if lang == MARKDOWN_KERNEL:
                post += '\n'
                self.prev_was_md = True
            else:
                post += '```{{{opt}}}\n'
                self.prev_was_md = False

        # process output pattern:
        return (pre + post).format(opt=preprocess_options(opt))


def knitty_preprosess(source: str, lang: str=None) -> str:
    """
    Stitch options preprocess function.

    Also converts document with Hydrogen code cells
    to markdown document with code chunks.

    :param source: str
    :param lang: str
        Default language
    :return: str
        New source
    """
    rep = Replacer(lang)
    cells_mode = SEARCH.HYDRO_FIRST_LINE.match(source)
    if cells_mode:
        comm = re.escape(cells_mode.group('COMM'))
        block_begin = cells_mode.group('BEGIN')
        block_end = cells_mode.group('END')
        if block_begin is None:
            hydro_regex = SEARCH.HYDRO.format(comm=comm, opt=SEARCH.OPT)
        else:
            hydro_regex = SEARCH.HYDRO_BLOCK_COMM.format(begin=re.escape(block_begin), end=re.escape(block_end),
                                                         comm=comm, opt=SEARCH.OPT)
            rep.use_block_comm = True
        # regex assumes new line at the end:
        return re.sub(hydro_regex, rep.replace_cells, source + '\n')
    else:
        return re.sub(SEARCH.PATTERN, rep.replace, source)


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
    # language=PythonRegExp
    _ARG = r'(?P<ARG>{key})'.format(key=KEY)  # language=PythonRegExp
    _DELIM = r'(?P<DELIM>{_},{_})'.format(_=SPACE)  # language=PythonRegExp
    KWARG = r'(?P<KWARG>(?P<KEY>{key}){_}={_}(?P<VAL>{val}))'.format(key=KEY, val=VAL, _=SPACE)

    PATTERN = re.compile('|'.join([KWARG, _ARG, _DELIM]))
    NAME = re.compile(r'^{key}$'.format(key=KEY))


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
