# Knitty

[![Build Status](https://travis-ci.org/kiwi0fruit/knitty.svg?branch=master)](https://travis-ci.org/kiwi0fruit/knitty)

Knitty is a Pandoc filter and [Atom/Hydrogen](https://atom.io/packages/hydrogen)-friendly reproducible report generation tool via Jupyter, Pandoc and Markdown (fork of the [Stitch](https://github.com/kiwi0fruit/knitty/blob/master/docs/stitch.md) that is a [Knitr](http://yihui.name/knitr/)-[RMarkdown](http://rmarkdown.rstudio.com)-like library in Python). Insert python code (or other Jupyter kernel code) to the Markdown document **or write in plain Python/Julia/R with block-commented Markdown** and have code's results in the Pandoc output document.

See [**Knitty documentation**](https://github.com/kiwi0fruit/knitty/blob/master/docs/knitty.md).

You can use:

* [Pandoc >=2.6](https://pandoc.org/MANUAL.html#creating-jupyter-notebooks-with-pandoc) to export to .ipynb notebooks (optionally: [install Pandoc in Python](https://github.com/kiwi0fruit/py-pandoc)),
* [ipynb-py-converter](https://github.com/kiwi0fruit/ipynb-py-converter) to convert .ipynb to .py to use with Knitty.


## Install

Install as part of [Pandoctools](https://github.com/kiwi0fruit/pandoctools) - convenient interface and works out of the box.

Needs Python 3.6+ but you can have other versions via Jupyter kernels as Knitty can use any installed kernel.

Via conda:
```bash
conda install -c defaults -c conda-forge knitty
```

Via pip:

```bash
pip install knitty
```

See additional info about how to install Jupyter kernels in Conda environments [**here**](https://github.com/kiwi0fruit/pandoctools/blob/master/docs/tips.md).


### Atom/Hydrogen

Knitty is much better to be used with something like Atom/Hydrogen. See [Best Python/Jupyter/PyCharm experience + report generation with Pandoc filters](https://github.com/kiwi0fruit/pandoctools/blob/master/docs/best_python_jupyter_pycharm_experience.md) for more details. You can also try VS Code interface to Jupyter from [vscode-python](https://github.com/Microsoft/vscode-python) instead of Atom/Hydrogen. I highly recommend to try to think about ipynb as merely an output format like pdf (albeit dynamic and rich) instead of main format or intermediate format.


### Optional install

Modified version of [Notedown](https://github.com/kiwi0fruit/knitty/blob/master/docs/notedown.md) by Aaron O'Leary is included in Knitty as `knotedown`.
If you would like to use `knotedown` to import from R Markdown you need installed `knitr`:

```bash
conda install r-knitr r-reticulate
```


## Usage

You either can use Knitty as a standard Pandoc filter:

```bash
cat doc.md | pre-knitty | pandoc --filter knitty -o doc.ipynb
```
and specify some subset of Knitty options in metadata: `self_contained: True`, `standalone: True`. But this way you cannot switch from Markdown to RST for example.

Or you can set all Knitty options (including those in metadata) by using it as a Pandoc filter with multiple arguments. Knitty is intended to be used in Pandoctools bash profiles (so it's CLI is split-up) but you can easily use Knitty independently. You should only **save and tweak** shell script for this. There is a Bash example below. If on Windows I strongly recommend to install [Git together with Bash](https://git-scm.com/downloads).

`./metadata.yaml`:
```yaml
---
kernels-map:
  r: ir
  py: python
styles-map:
  py: python
comments-map:
  py: ['#', "'''", "'''", "\"\"\"", "\"\"\""]
  js: ["//", "/*", "*/"]
  ts: ["//", "/*", "*/"]
  r: ['#', "'", "'", "\"", "\""]
...
```

`./knitty`:
```bash
#!/bin/bash
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export LANG=C.UTF-8
export PYTHONIOENCODING=utf-8

in="$1"
yml="$here/metadata.yaml"
R=(-f markdown)
W=(-t html --standalone --self-contained)

t="$(pandoc-filter-arg "${W[@]}")"
cat "$in" |
pre-knitty "$in" --yaml "$yml" |
cat - <(printf "\n\n") "$yml" |
pandoc "${R[@]}" -t json |
knitty $t "$in" "${R[@]}" "${W[@]}" |
pandoc -f json "${W[@]}" -o "$in.html"
```
(`$t` is an arg that Pandoc passes to it's filters).

Then use it like `./knitty /path/to/doc.py` that would save `/path/to/doc.py.html`.


### Batch example

And if you don't like Bash there is a Windows batch example below (see [setvar](https://github.com/kiwi0fruit/knitty/blob/master/examples/setvar.bat)):
```bat
chcp 65001 > NUL
set PYTHONIOENCODING=utf-8

set in=doc.md
set R=-f markdown
set W=-t html --standalone --self-contained

pandoc-filter-arg %W% | call .\setvar t
type "%in%" | pre-knitty | ^
pandoc %R% -t json | ^
knitty %t% "%in%" %R% %W% | ^
pandoc -f json %W% -o "%in%.html"
```


### To ipynb conversion

Before v0.5.0 Knitty supported conversion to .ipynb via Notedown but since v0.5.0 it is adapted to be used with Pandoc >=2.6. You can learn how to convert to ipynb via Pandoc [**here**](https://pandoc.org/MANUAL.html#creating-jupyter-notebooks-with-pandoc) (optionally: [install Pandoc in Python](https://github.com/kiwi0fruit/py-pandoc)). I also recommend using `knitty.self_contained_raw_html_img` Panflute filter (see [here](https://github.com/kiwi0fruit/knitty/blob/master/docs/knitty.md#self_contained_raw_html_img-panflute-filter)) to fix Pandoc attachments created when to .ipynb conversion.


### Using with pandoc-crossref

Worth mentioning that you can use Knitty together with [pandoc-crossref](https://github.com/lierdakil/pandoc-crossref) (see [install instructions](https://github.com/kiwi0fruit/py-pandoc-crossref)). You may also need to tune output format in Pandoc and execute the notebook. See example without Knitty:

```bash
pandoc doc.md --filter pandoc-crossref --to "ipynb-bracketed_spans-fenced_divs\
-link_attributes-simple_tables-multiline_tables-grid_tables-pipe_tables\
-fenced_code_attributes-markdown_in_html_blocks-table_captions-smart" | \
jupyter nbconvert --to notebook --execute --stdin --stdout > doc.ipynb
```
