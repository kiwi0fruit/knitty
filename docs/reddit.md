# Knitty: Jupyter power in plain Python/Julia/R/any kernel lang. Pandoc filter and Atom/Hydrogen friendly literature programming (Stitch fork)

(*__backup of__ [__the reddit post__](https://www.reddit.com/r/datascience/comments/b061up/knitty_jupyterpandocide_power_in_plain/)*)

[**Knitty**](https://github.com/kiwi0fruit/knitty) is a Pandoc filter and [Atom/Hydrogen](https://atom.io/packages/hydrogen)-friendly reproducible report generation tool via Jupyter, Pandoc and Markdown (fork of the [Stitch](https://github.com/kiwi0fruit/knitty/blob/master/docs/stitch.md) that is a [Knitr](http://yihui.name/knitr/)-[RMarkdown](http://rmarkdown.rstudio.com)-like library in Python). Insert python code (or other Jupyter kernel code) *to the Markdown document* **or write in plain Python/Julia/R with block-commented Markdown** and have code's results in the Pandoc output document.

Knitty is an important part of the [Best Python/Jupyter/PyCharm experience + report generation with Pandoc filters](https://github.com/kiwi0fruit/pandoctools/blob/master/docs/best_python_jupyter_pycharm_experience.md) (see there why writing in plain Python/Julia/R is great) but actually

Knitty is language agnostic and can be used with any Jupyter kernel. Can be used independently of Pandoctools and with any IDE of choise. So I guess it deserves a separate post. By the way: Atom/Hydrogen is also language agnostic. You can also try **VS Code** interface to Jupyter from [**vscode-python**](https://github.com/Microsoft/vscode-python) instead of Atom/Hydrogen. I highly recommend to try to think about ipynb as merely an output format like pdf instead of main format or intermediate format (albeit ipynb is great for presenting narrative interactively and it can even [be much more](https://github.com/kiwi0fruit/misc/blob/master/src/pdf_and_word_killer.md)). 

[**knitty repo**](https://github.com/kiwi0fruit/knitty).


### P.S.

[Knitty vs. Knitpy](https://github.com/kiwi0fruit/knitty/issues/1) joke.
