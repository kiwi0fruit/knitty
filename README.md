# Knitty

Knitty is another CLI for Stitch/Knotr: reproducible report generation tool via Jupyter, Pandoc and Markdown. Insert python code (or other Jupyter kernel code) to the Markdown document and have code's results in the output document.

See [Knitty documentation](https://github.com/kiwi0fruit/knitty/blob/master/knitty.md)


## Install

```sh
pip install knitty
```

If you use conda package manager (Anaconda/Miniconda) then you can install dependencies first:

```sh
conda install -c defaults -c conda-forge jupyter_core traitlets ipython jupyter_client nbconvert pandocfilters pypandoc click psutil "pandoc>=2.0"
```
Pandoc ≥ 2.0 is needed for proper Knitty output re-processing. In particular for nested HTML insertions to Markdown for toolchain: `file.md` → `file.md.md` → `file.md.md.html`.

Also can install from GitHub:

```sh
pip install git+https://github.com/kiwi0fruit/knitty.git
```
In this case you need to have installed [Git](https://git-scm.com/downloads) available from command prompt.

<!-- pandoc README.md -o README.rst -->