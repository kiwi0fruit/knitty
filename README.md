# Knitty

[![Build Status](https://travis-ci.org/kiwi0fruit/knitty.svg?branch=master)](https://travis-ci.org/kiwi0fruit/knitty)

Knitty is a Pandoc filter and Atom/Hydrogen friendly inrterface wrapper for [Stitch/Knotr](https://github.com/kiwi0fruit/knitty/blob/master/docs/stitch.md): reproducible report generation tool via Jupyter, Pandoc and Markdown. Insert python code (or other Jupyter kernel code) to the Markdown document and have code's results in the output document. Exports to Jupyter notebook via [Notedown](https://github.com/kiwi0fruit/knitty/blob/master/docs/notedown.md).

See [Knitty documentation](https://github.com/kiwi0fruit/knitty/blob/master/docs/knitty.md).

You can use [vscode-ipynb-py-converter](https://github.com/nojvek/vscode-ipynb-py-converter) to convert .ipynb to .py to use with Knitty.


## Install

Install as part of [Pandoctools](https://github.com/kiwi0fruit/pandoctools) - convenient interface and works out of the box.

Needs Python 3.6+ but you can have other versions via Jupyter kernels as Knitty can use any installed kernel.

Or install on Windows (if you use conda package manager (Anaconda/Miniconda) then you can install dependencies first):
```bash
conda install -c defaults -c conda-forge "pip>=10.0.1" "pandoc>=2.2.1" jupyter_core ^
traitlets ipython jupyter_client nbconvert pandocfilters pypandoc click psutil nbformat ^
pandoc-attributes pyyaml
pip install knitty
```

If pip install fails try to change codepage: `chcp 1252`.

On Unix:
```bash
conda install -c defaults -c conda-forge "pip>=10.0.1" "pandoc>=2.2.1" jupyter_core \
traitlets ipython jupyter_client nbconvert pandocfilters pypandoc click psutil nbformat \
pandoc-attributes pyyaml
pip install knitty
```

Pandoc ≥ 2.0 is needed for proper Knitty output re-processing. In particular for nested HTML insertions to Markdown for toolchain: `file.md` → `file.md.md` → `file.md.md.html`. Pandoc 2.1.\* does not works on windows.


### Optional install

If you would like to use `knotedown` to import from R Markdown you need installed `knitr`:

```bash
conda install r-knitr r-reticulate
```


## Usage

Unix:
```bash
export PYTHONIOENCODING=utf-8

input_file="doc.md"
metadata="metadata.yml"
reader_args=(-f markdown)
writer_args=(-t html --standalone --self-contained)

cat "${input_file}" | \
pre-knitty "${input_file}" --yaml "$metadata" | \
pandoc "${reader_args[@]}" -t json | \
knitty "${input_file}" "${reader_args[@]}" "${writer_args[@]}" | \
pandoc -f json "${writer_args[@]}" -o "${input_file}.html"
```

Windows:
```bat
chcp 65001 > NUL
set PYTHONIOENCODING=utf-8

set input_file=doc.md
set metadata=metadata.yml
set reader_args=-f markdown
set writer_args=-t html --standalone --self-contained

type "%input_file%" | ^
pre-knitty "%input_file%" --yaml "%metadata%" | ^
pandoc %reader_args% -t json | ^
knitty "%input_file%" %reader_args% %writer_args% | ^
pandoc -f json %writer_args% -o "%input_file%.html"
```

Jupyter kernel specification in metadata section:
```yaml
---
kernelspec:
  display_name: R
  language: R
  name: ir
...
```

Export to Jupyter notebook with cross-references (using [pandoc-crossref](https://github.com/lierdakil/pandoc-crossref): [download](https://github.com/lierdakil/pandoc-crossref/releases)) and execute it:

```bash
export PYTHONIOENCODING=utf-8

input_file="doc.md"
metadata="metadata.yml"
reader_args=(-f markdown)
jupymd="markdown-bracketed_spans-fenced_divs-link_attributes-simple_tables\
-multiline_tables-grid_tables-pipe_tables-fenced_code_attributes\
-markdown_in_html_blocks-table_captions-smart"
writer_args=(-t "$jupymd" --standalone --self-contained --filter pandoc-crossref)

cat "${input_file}" | \
pre-knitty "${input_file}" --yaml "$metadata" | \
pandoc "${reader_args[@]}" -t json | \
knitty "${input_file}" "${reader_args[@]}" "${writer_args[@]}" --to-ipynb | \
pandoc -f json "${writer_args}" | \
post-knitty --to-ipynb | \
jupyter nbconvert --to notebook --execute --stdin --stdout > \
"${input_file}.ipynb"
```
