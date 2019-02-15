# Knitty

[![Build Status](https://travis-ci.org/kiwi0fruit/knitty.svg?branch=master)](https://travis-ci.org/kiwi0fruit/knitty)

Knitty is a Pandoc filter and Atom/Hydrogen friendly inrterface wrapper for [Stitch/Knotr](https://github.com/kiwi0fruit/knitty/blob/master/docs/stitch.md): reproducible report generation tool via Jupyter, Pandoc and Markdown. Insert python code (or other Jupyter kernel code) to the Markdown document and have code's results in the output document. Exports to Jupyter notebook via [Notedown](https://github.com/kiwi0fruit/knitty/blob/master/docs/notedown.md).

See [Knitty documentation](https://github.com/kiwi0fruit/knitty/blob/master/docs/knitty.md).

You can use [ipynb-py-converter](https://github.com/kiwi0fruit/ipynb-py-converter) to convert .ipynb to .py to use with Knitty.


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

If you would like to use `knotedown` to import from R Markdown you need installed `knitr`:

```bash
conda install r-knitr r-reticulate
```


## Usage

You either can use Knitty as a standard Pandoc filter:

```bash
cat doc.md | pre-knitty | pandoc --filter knitty -o doc.ipynb
```
and specify some subset knitty options (except dir) in metadata: `self_contained: True`, `standalone: True`. But this way you cannot switch from Markdown to RST for example.

Or you can set all Knitty options (incl. those in metadata) by using it as a Pandoc filter with multiple arguments (`$t` is an arg that Pandoc passes to it's filters):

Unix:
```bash
export PYTHONIOENCODING=utf-8
export LANG=C.UTF-8

input_file="doc.md"
metadata="metadata.yml"
reader_args=(-f markdown)
writer_args=(-t html --standalone --self-contained)

t="$(pandoc-filter-arg "${writer_args[@]}")"
cat "${input_file}" | \
pre-knitty "${input_file}" --yaml "$metadata" | \
pandoc "${reader_args[@]}" -t json | \
knitty $t "${input_file}" "${reader_args[@]}" "${writer_args[@]}" | \
pandoc -f json "${writer_args[@]}" -o "${input_file}.html"
```

Windows (see [setvar](https://github.com/kiwi0fruit/enaml-video-app/blob/master/enaml-video-app/setvar.bat)):
```bat
chcp 65001 > NUL
set PYTHONIOENCODING=utf-8

set input_file=doc.md
set metadata=metadata.yml
set reader_args=-f markdown
set writer_args=-t html --standalone --self-contained

pandoc-filter-arg %writer_args% | call .\setvar t
type "%input_file%" | ^
pre-knitty "%input_file%" --yaml "%metadata%" | ^
pandoc %reader_args% -t json | ^
knitty %t% "%input_file%" %reader_args% %writer_args% | ^
pandoc -f json %writer_args% -o "%input_file%.html"
```

Before v0.5.0 Knitty supported conversion to ipynb via Notedown but since v0.5.0 it is adapted to be used with Pandoc >=2.6. You can learn how to convert to ipynb via Pandoc [**here**](https://pandoc.org/MANUAL.html#creating-jupyter-notebooks-with-pandoc).

Worth mentioning that you can use it together with [pandoc-crossref](https://github.com/lierdakil/pandoc-crossref) (see [install instructions](https://github.com/kiwi0fruit/py-pandoc-crossref)). You may also need to tune output format in Pandoc and execute the notebook. See example without Knitty:

```bash
pandoc doc.md -F pandoc-crossref --to "ipynb-bracketed_spans-fenced_divs\
-link_attributes-simple_tables-multiline_tables-grid_tables-pipe_tables\
-fenced_code_attributes-markdown_in_html_blocks-table_captions-smart" | \
jupyter nbconvert --to notebook --execute --stdin --stdout > doc.ipynb
```
