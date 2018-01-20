# Knitty

Knitty is Atom/Hydrogen friendly CLI for Stitch/Knotr: reproducible report generation tool via Jupyter, Pandoc and Markdown. Insert python code (or other Jupyter kernel code) to the Markdown document and have code's results in the output document.

Modified version of Knotr/Stitch by Tom Augspurger is included in Knitty. [Original version](https://github.com/pystitch/stitch).


# Contents

* [Knitty usage](#knitty-usage)
* [Differences from original Stitch:](#differences-from-original-stitch)
1. [New interfaces](#1-new-interfaces)
    * [1.1 New command line interfaces][new_cli]
    * [1.2 Alternative settings placement][alt_settings]
    * [1.3 Support files with Atom/Hydrogen code cells][code_cells]
    * [1.4 Turn ON code cells mode](#14-turn-on-code-cells-mode)
    * [1.5 Other languages in code cells mode](#15-other-languages-in-code-cells-mode)
    * [1.6 Markdown in code cells mode](#16-markdown-in-code-cells-mode)
    * [1.7 Example python file in code cells mode][code_cells_example]
2. [New code chunks options](#2-new-code-chunks-options)
    * [2.1 Original code chunk options](#21-original-code-chunk-options)
    * [2.2 Results Pandoc chunk option](#22-results-pandoc-chunk-option)
    * [2.3 Chunk keyword argument](#23-chunk-keyword-argument)
3. [New document options](#3-new-document-options)
    * [3.1 Original document options](#31-original-document-options)
    * [3.2 Disabled code chunks prompt prefixes](#33-disabled-code-chunks-prompt-prefixes)
    * [3.3 Languages / Kernels / Styles mappings in YAML metadata](#34-languages-kernels-styles-mappings-in-yaml-metadata)
4. [API description](#4-api-description)
5. [Known issues](#5-known-issues)
    * [5.1 No new line after Jupyter output](#51-no-new-line-after-jupyter-output)
    * [5.2 Pandoc-crossref labels move to the new line](#52-pandoc-crossref-labels-move-to-the-new-line)

[alt_settings]: #12-alternative-settings-placement
[new_cli]: #11-new-command-line-interfaces
[code_cells]: #13-support-files-with-atom-hydrogen-code-cells
[code_cells_example]: #17-example-python-file-in-code-cells-mode


# Knitty usage

You can use Hydrogen/Knitty combo to write Markdown documents with Jupyter code chunks (you can use any Jupyter kernel). You can execute code chunks with Atom/Hydrogen right when writing the document and instantly see the results. Knitty helps to export the whole document to other format (html, pdf, output self-contained markdown).

* Write Markdown document: [1.2 Alternative settings placement][alt_settings]
* Write Atom/Hydrogen code cells document: [1.7 Example python file in code cells mode][code_cells_example]

Tip: see how to [install and use Hydrogen Atom package](hydrogen.md).


# Differences from original Stitch:

# 1. New interfaces

New interfaces are exclusive to Knitty.

## 1.1 New command line interfaces

`pre-knitty` - CLI app that reads from stdin. Transforms markdown source code from Knitty format to Pandoc format (replaces Knitty-format code chunk options with Pandoc-format code chunk options). And writes to stdout.

* first argument is optional input file path (`pre-knitty` reads it's extension that is needed for [code cells][code_cells] mode).

`knitty` - CLI app that is a Pandoc AST filter that reads from stdin and writes to stdout (but it has arguments and options).

* first argument is an optional input file path that helps to auto-name Knitty data folder in some cases.
* Options:
    * `-f TEXT`, `-r TEXT`, `--from TEXT`, `--read TEXT` – Pandoc reader option. Specify input format,
    * `-o TEXT`, `--output TEXT` – Pandoc writer option. Optional but it helps to auto-name Knitty data folder in some cases,
    * `-t TEXT`, `--to TEXT`, `-w TEXT`, `--write TEXT` – Pandoc writer option. Optional but it helps to auto-name Knitty data folder in some cases,
    * `--standalone` – Pandoc writer option. Produce a standalone document instead of fragment,
    * `--self-contained` – Pandoc writer option. Store resources like images inside document instead of external files,
    * `--dir-name TEXT` – Manually name Knitty data folder (instead of default auto-naming).

Examples:

```sh
input_file="doc.md"
reader_args=(-f markdown)
writer_args=(-t html --standalone --self-contained)
cat "${input_file}" | pre-knitty "${input_file}" | pandoc "${reader_args[@]}" -t json | knitty "${input_file}" "${reader_args[@]}" "${writer_args[@]}" | pandoc -f json "${writer_args[@]}" -o "${input_file}.html"
```

```bat
set input_file=doc.md
set reader_args=-f markdown
set writer_args=-t html --standalone --self-contained
type %input_file% | pre-knitty %input_file% | pandoc %reader_args% -t json | knitty %input_file% %reader_args% %writer_args% | pandoc -f json %writer_args% -o %input_file%.html
```

`knotedown` - [patched Notedown module](https://github.com/kiwi0fruit/notedown) by Aaron O'Leary (aaren) was added to Knitty and available via `knotedown` CLI - same API as in `notedown` CLI. Patched version support Pandoc metadata that is then set in notebook metadata. For example:

```yaml
---
kernelspec:
  display_name: Python 3
  language: python
  name: python3
...
```

```yaml
---
kernelspec:
  display_name: R
  language: R
  name: ir
...
```

Example:

```bat
set writer_args=--standalone --self-contained -t markdown-fenced_code_attributes
type test.md | pandoc -f markdown -t json | pre-notedown | pandoc -f json %writer_args% | knotedown --match=in > test.ipynb
```

(`--standalone --self-contained -t markdown-fenced_code_attributes` are necessary for conversion). 


## 1.2 Alternative settings placement

Alternative Knitty settings placement was added for GitHub flavored markdown (GFM) compatibility in Atom editor (**language-gfm** compatibility with working spell checking).

Standard Knitty options inside decorator (`python` will overwrite `py`):
`````python
Markdown text.

@{python, chunk1, echo=True}
```py
print('Hello!')
```

More markdown text.
`````

Language specified in the code chunk so the decorator has only keyword arguments:
`````python
@{chunk=chunk2, echo=True}
```python
print('Hello!')
```
`````

Standard RMarkdown-like Knotr/Stitch options also works:
`````python
```{python, chunk3, echo=True}
print('Hello!')
```
`````

Or simply:
`````python
```python
print('Hello!')
```
`````

**Please note** that Knitty converts Knitty-style and Stitch-style options (that are originally not supported by Pandoc parser) to Pandoc-style options. When converting Knitty also add `eval=True` like: <code>\`\`\`{python, eval=True}</code> to <code>\`\`\`{.python eval=True}</code>.

Specifics:

* There can't be any white spaces between `@` and `{...}`. But there can be whitespace characters between <code>\`\`\`</code> and `{...}` (all whitespace characters except `\r` and `\n` actually).
* Chunk options arguments and keys should start with alphabetic characters or `_` and can contain alphanumeric characters, `-`, and `.` (but can't end with a `.`).  
* Key values may be put into `''` or `""` but should match the following regex:

```
"[^"]*"|'[^']*'|[^\s,{}"'][^\s,{}]*
```
* Please note that the following settings `@{ir, class=r}` are equivalent to `@{ir, r}` that is equivalent to <code>\`\`\`{.ir .r}</code> (this is because for Pandoc `class=c` attribute is the same as `.c` setting). So `r` would be a chunk name.


## 1.3 Support files with Atom/Hydrogen code cells

Added support for files with Atom/Hydrogen code cells (**.py** extension). You can split the file into code cells via in-line comments with <code> %% </code>:
```py
# %% {chunk=chunk2, echo=False} comment text
```
(for python). Knitty will convert such python code cells to markdown code chunks and then convert to output format (md / html / pdf).

Such files for example can be edited in Atom/Hydrogen or in PyCharm.

**Code cells mode is language-agnostic so you can use any Jupyter kernel.**


## 1.4 Turn ON code cells mode

In order to tell Knitty that the file should be treated as raw code you should do the following: The first line should start with 1-3 symbols of the in-line comment (except white spaces), then single white space, then `%%`, then single white space or end of line. So you actually tell Knitty what symbols are used as in-line comments.

For python it would be `# %%` comments. Also you can specify Knitty settings: `# %% {python, echo=False}`. If no settings specified or no language specified - `# %% {echo=False}` - then the language would be the file extension.


## 1.5 Other languages in code cells mode

You can insert code cells of other languages to the **.py** file with python main language (for example via `# %% {r}`). They optionally may be put inside block comments. In order to automatically remove such comments first you should specify block comments settings in the very first line of the file. Python example:

```python
# %% {md} """ %%% """
```

That should be valid code cell line with optional but valid Knitty options. Then space, then 1-6 symbols of block comment opening (except white spaces), then single white space, then `%%%`, then single white space, then 1-6 symbols of block comment closing (except white spaces), then white space or end of line. So you actually tell Stitch what symbols are used as block comments.

For example for python: if after `# %%` line the very next one is `"""` then that next one is omitted. If the opening block comment was omitted then the closing block comment is omitted if after `"""` line there are only white spaces or newlines before new `# %%` or the end of file (but there should be at least one newline).


## 1.6 Markdown in code cells mode

Code cell can be in markdown as well. It's the `md` language. You can use them to define Knitty metadata.

## 1.7 Example python file in code cells mode

Example python file:

```python
# %% {md} """ %%% """ Markdown cell that doesn't affect PyCharm code inspection and Hydrogen `Run All`:
"""
---
kernels-map:
  r: ir
  py: python
...

# Markdown section title

Here is some markdown text.
"""

# %% {echo=False} `py` cell, language name is taken from file extension:
import math
print('This was {py, echo=False} cell')

# %%

"""
Comment that stays after Knitty
because it's not right after `# %%`
"""
print('Block comments test')

# %% {r} R cell:
"""
x <- c(10, 20)
x[1]
"""

# %% {results=pandoc}
print('''

Another markdown text. Now with SugarTeX formula: ˎα^˱{pi:1.3f}˲ˎ.
It works because of the `results=pandoc` option and `sugartex` Pandoc filter.

'''.replace('ˎ', '$').format(pi=math.pi))
```


# 2. New code chunks options

## 2.1 Original code chunk options

See Knotr/Stitch code chunks options [here](https://pystitch.github.io/api.html#chunk-options).

Notable options:

* `eval=True`, `eval=False`: whether to execute the code chunk. As well as all other chunk options, default for all chunks `eval` option can be set is yaml metadata section:

```yaml
---
eval: True
...
```


## 2.2 Results Pandoc chunk option

`results` code chunk option was modified:

* default is `results=default` (same as in the original Stitch),
* `results=pandoc`: same as `default` but some Jupyter output is parsed as markdown: if the output is a stdout message that is not warning/error or if it has `text/plain` key. For example python `print()` output.
* `results=hide`: evaluate chunk but hide results (same as in the original Stitch).


## 2.3 Chunk keyword argument

Added `chunk=name` new keyword argument option. It's an alternative way to specify code chunk name (together with second positional argument. Keyword argument has a priority over it).

This option is exclusive to Knitty.


# 3. New document options

## 3.1 Original document options

See Knotr/Stitch document options [here](https://pystitch.github.io/api.html#api) (some of the options are chunk options actually).


## 3.2 Disabled code chunks prompt prefixes

Now code chunk prefixes are disabled by default. To enable them set it in the metadata section:

```yaml
---
use_prompt: True
...
```

If you specify `prompt` option for a code chunk then it would have a prompt even if it's disabled.


## 3.3 Languages / Kernels / Styles mappings in YAML metadata

Mappings to markdown YAML metadata are added:

* from **language names** to **Jupyter kernels names**
* from **language names** to **CSS classes names**
* **language names** are used in Stitch code blocks settings

For example:

```yaml
---
kernels-map:
  r: ir
  py2: python2
styles-map:
  py2: py
...
```


# 4. API description

`stitch.Stitch` class API description should be changed a bit:

```py
class Stitch(HasTraits):
    ...
    def __init__(self, name: str, to: str='html',
                 standalone: bool=True,
                 self_contained: bool=True,
                 warning: bool=True,
                 error: str='continue',
                 prompt: str=None,
                 use_prompt: bool=False,
                 pandoc_extra_args: list=None):
        """
        Parameters
        ----------
        name : str
            controls the directory for supporting files
        to : str, default ``'html'``
            output format
        standalone : bool, default True
            whether to make a standalone document
        self_contained: bool, default True
        warning : bool, default True
            whether to include warnings (stderr) in the ouput.
        error : ``{"continue", "raise"}``
            how to handle errors in the code being executed.
        prompt : str, default None
        use_prompt : bool, default False
            Whether to use prompt prefixes in code chunks
        pandoc_extra_args : list of str, default None
            Pandoc extra args for converting text from markdown
            to JSON AST.
        """
        ...

    def stitch_ast(self, ast: dict) -> dict:
        """
        Main method for converting a document.

        Parameters
        ----------
        ast : dict
            Loaded Pandoc json AST

        Returns
        -------
        doc : dict
            These should be compatible with pandoc's JSON AST
            It's a dict with keys
              - pandoc-api-version
              - meta
              - blocks
        """
        ...

```


# 5. Known issues

## 5.1 No new line after Jupyter output

Sometimes R language output does not have new line after it (or may be other languages as well). So it might interfere with the next text. Adding

```html
<b></b>
```

below the code chunk fixes the problem.


## 5.2 Pandoc-crossref labels move to the new line

When you add formula labels for **pandoc-crossref** you should place them right after the formula (like `$$x=y+z$${#eq:1}` – no spaces). Otherwise when stitching from markdown to markdown labels would move to the next line and stop working.
