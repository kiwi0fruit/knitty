Knitty
======

Knitty is Atom/Hydrogen friendly inrterface wrapper for Stitch/Knotr:
reproducible report generation tool via Jupyter, Pandoc and Markdown.
Insert python code (or other Jupyter kernel code) to the Markdown
document and have code’s results in the output document.

See `Knitty
documentation <https://github.com/kiwi0fruit/knitty/blob/master/knitty.md>`__.

Install
-------

.. code:: sh

    pip install knitty

If you use conda package manager (Anaconda/Miniconda) then you can
install dependencies first:

.. code:: sh

    conda install -c defaults -c conda-forge "pandoc>=2.0,<2.1" jupyter_core traitlets ipython jupyter_client nbconvert pandocfilters pypandoc click psutil

Pandoc ≥ 2.0 is needed for proper Knitty output re-processing. In
particular for nested HTML insertions to Markdown for toolchain:
``file.md`` → ``file.md.md`` → ``file.md.md.html``.

Also can install from GitHub:

.. code:: sh

    pip install git+https://github.com/kiwi0fruit/knitty.git

In this case you need to have installed
`Git <https://git-scm.com/downloads>`__ available from command prompt.

Usage
-----

Unix:

.. code:: sh

    input_file="doc.md"
    reader_args=(-f markdown)
    writer_args=(-t html --standalone --self-contained)
    cat "${input_file}" | pre-knitty "${input_file}" | pandoc "${reader_args[@]}" -t json | knitty "${input_file}" "${reader_args[@]}" "${writer_args[@]}" | pandoc -f json "${writer_args[@]}" -o "${input_file}.html"

Windows:

.. code:: bat

    set input_file=doc.md
    set reader_args=-f markdown
    set writer_args=-t html --standalone --self-contained
    type %input_file% | pre-knitty %input_file% | pandoc %reader_args% -t json | knitty %input_file% %reader_args% %writer_args% | pandoc -f json %writer_args% -o %input_file%.html

Jupyter kernel specification in metadata section:

.. code:: yaml

    ---
    kernelspec:
      display_name: R
      language: R
      name: ir
    ...

Export to Jupyter notebook:

.. code:: bat

    set writer_args=--standalone --self-contained -t markdown-fenced_code_attributes
    type test.md | pandoc -f markdown -t json | pre-notedown | pandoc -f json %writer_args% | knotedown --match=in > test.ipynb
