Whatsnew
========

Version 0.3.5
`````````````

- Bug: Fixed a bug where empty messages from the IR kernel
  would crash the parser (:issue:`52`).


Version 0.3.4
`````````````

Version 0.3.4 is a minor release from 0.3.3;
It contains several bug fixes and several new chunk options for controlling
the output.

- BUG: Fixed a bug in the chunk options-line parser where arguments like ``fig.cap="Figure, captioned"``, quoted strings
  containing a comma, would break the parser (:issue:`42`)
- API: Accept ``fig.cap`` as a chunk option to control the figure caption (:issue:`38`)
- API: Exposed the ``no-self-contained`` command-line option to the stitching
  operation.
- API: Added a ``warning`` option for controling whether stderr is included in the output.
- API: Changed the ``on_error`` option to ``error`` for compatability with knitr and symmytry with the ``warning`` option.
- BUG: Various issues with javascript output (e.g. Bokeh plots) have been fixed (:issue:`46`).
- ENH: The configuration system has been overhauled, so you should be able to set
  options at either the command-line, document metadata, or chunk level (:issue:`36`)

Version 0.3.3
`````````````

- Included ``default.css`` in the source and binary distributions (:issue:`26`).
- Fixed not handling output from IPython's various ``display`` methods (:issue:`27`).
