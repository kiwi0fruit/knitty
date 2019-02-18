# Knitty

[![Build Status](https://travis-ci.org/kiwi0fruit/knitty.svg?branch=master)](https://travis-ci.org/kiwi0fruit/knitty)

Knitty is a Pandoc filter and Atom/Hydrogen-friendly reproducible report generation tool via Jupyter, Pandoc and Markdown (fork of the [Stitch](stitch.md)). Insert python code (or other Jupyter kernel code) to the Markdown document and have code's results in the output document.

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


### Optional install

Modified version of [Notedown](notedown.md) by Aaron O'Leary is included in Knitty as `knotedown`.
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

Or you can set all Knitty options (including those in metadata) by using it as a Pandoc filter with multiple arguments (`$t` is an arg that Pandoc passes to it's filters):

Unix:
```bash
export LANG=C.UTF-8
export PYTHONIOENCODING=utf-8

in=doc.md
R=(-f markdown)
W=(-t html --standalone --self-contained)

t="$(pandoc-filter-arg "${W[@]}")"
cat "$in" | pre-knitty |
pandoc "${R[@]}" -t json |
knitty $t "$in" "${R[@]}" "${W[@]}" |
pandoc -f json "${W[@]}" -o "$in.html"
```

Windows (see [setvar](https://github.com/kiwi0fruit/knitty/blob/master/examples/setvar.bat)):
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

Before v0.5.0 Knitty supported conversion to ipynb via Notedown but since v0.5.0 it is adapted to be used with Pandoc >=2.6. You can learn how to convert to ipynb via Pandoc [**here**](https://pandoc.org/MANUAL.html#creating-jupyter-notebooks-with-pandoc) (optionally: [install Pandoc in Python](https://github.com/kiwi0fruit/py-pandoc)).

Worth mentioning that you can use it together with [pandoc-crossref](https://github.com/lierdakil/pandoc-crossref) (see [install instructions](https://github.com/kiwi0fruit/py-pandoc-crossref)). You may also need to tune output format in Pandoc and execute the notebook. See example without Knitty:

```bash
pandoc doc.md -F pandoc-crossref --to "ipynb-bracketed_spans-fenced_divs\
-link_attributes-simple_tables-multiline_tables-grid_tables-pipe_tables\
-fenced_code_attributes-markdown_in_html_blocks-table_captions-smart" | \
jupyter nbconvert --to notebook --execute --stdin --stdout > doc.ipynb
```
