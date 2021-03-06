---
title: "Knitty: dynamic report generation with Python"
author: "Jan Schulz, Peter Zagubisalo"
date: "15.02.2019"
---

This is a port of Knitr (http://yihui.name/knitr/) and RMarkdown
(http://rmarkdown.rstudio.com/) to Python.

For a complete description of the code format see http://rmarkdown.rstudio.com/ and replace
`` ```{r...} `` by `` @{...}\n```python `` and of course use python code blocks...

## Examples

Here are some examples:

```python
print("Execute some code chunk and show the result")
```

Codechunks which contain lines without output (e.g. assign the result or comments) will
be shown in the same code block:

```python
# A comment
text = "All code in the same code block until some output is produced..."
more_text = "...and some more."
print(text)
print(more_text)
```

### Code chunk arguments

You can use different arguments in the codechunk declaration. Using `echo=False` will not show
the code but only the result.

@{echo=False}
```python
print("Only the output will be visible as `echo=False`")
```

The next paragraphs explores the code chunk argument `results`.

If 'hide', knitpy will not display the code's results in the final document. If 'hold', knitpy
will delay displaying all output pieces until the end of the chunk. If 'asis', knitpy will pass
through results without reformatting them (useful if results return raw HTML, etc.)

`results='hold'` is not yet implemented.

@{results=hide}
```python
print("Only the input is displayed, not the output")
```

@{results=pandoc, echo=False}
```python
print("This is formatted as markdown:\n**This text** will be bold...")
```

@{results=pandoc, echo=False}
```python
print("**This text** will be bold...")
```

**Note**: with python code it is recommended to use the IPython/Jupyter display system and an
appropriate wrapper (see below) to display such output and not `results=pandoc`. This makes it
possible to convert such output if the output can't be included in the final format.

You can also not show codeblocks at all, but they will be run:

@{echo=False}
```python
have_run = True
print("This will not be shown, as include is False")
```

@{echo=True}
```python
if have_run == True:
    print("'have_run==True': ran the codeblock before this one.")
```

Using `eval=False`, one can prevent the evaluation of the codechunk

```python
x = 1
```

@{eval=False}
```python
x += 1 # this is not executed as eval is False
```

```python
x # still 1
```


To remove/hide a codechunk completely, i.e. neither execute it nor show the code, you can use both `eval=False, echo=False`: nothing will be
shown between this text ...

@{eval=False, echo=False}
```python
x += 1 # this is not executed and not even shown
```

... and this text here!

### Inline code

You can use Python f-strings:

```python
from IPython.display import Markdown
Markdown(f'You can also include code inline: $m={1+1}$')
```
(expected: `$m=2$`)

### IPython / Jupyter display framework

The display framework is also supported.

Plots will be included as images and included in the document. The filename of the
plot is derived from the chunk label ("sinus" in this case). The code is not
shown in this case (`echo=False`).

@{chunk=sinus, echo=False}
```python
# As this all produces no output, it should go into the same input section...
import numpy as np
import matplotlib.pyplot as plt
y = np.linspace(2, 10)
line, = plt.plot(y, np.sin(y))
```

If a html or similar thing is displayed via the IPython display framework, it will be
included as is, meaning that apart from `text/plain`-only output, everything else
will be included without marking it up as output. Knitpy automagically tries to include only
formats which are understood by pandoc and the final output format (in some case converting the
format to one which the final output can handle).

```python
from IPython.display import display, HTML
display(HTML("<strong>strong text</strong>"))
```
`display()` is redundant.

It even handles `pandas.DataFrames` (be aware that not all formatting can be converted into all
output formats):

```python
import pandas as pd
pd.set_option("display.width", 200)
s = """This is longer text"""
df = pd.DataFrame({"a":[1,2,3,4,5],"b":[s,"b","c",s,"e"]})
df
```

`pandas.DataFrame` can be represented as `text/plain` or `text/html`, but will default to the html
 version. To force plain text, use either `print(df)` or set the right `pandas` option:

```python
pd.set_option("display.notebook_repr_html", False)
df
# set back the display
pd.set_option("display.notebook_repr_html", True)
```

You can also use package like [tabulate](https://bitbucket.org/astanin/python-tabulate)
together with `results=pandoc` or by wrapping it with the appropriate display class:

@{results=pandoc}
```python
from tabulate import tabulate
# either print and use `results=pandoc`
print(tabulate(df, list(df.columns), tablefmt="simple"))
```

```python
from tabulate import tabulate
from IPython.display import Markdown
# or use the IPython display framework to publish markdown
Markdown(tabulate(df, list(df.columns), tablefmt="simple"))
```
