# %% 
"""
---
# test start with and without r'^# %%'
knitty:
  comments: ['#', "'''", "'''", "\"\"\"", "\"\"\""]
...
"""

# %% {r, echo=False}
'''print(0)'''

# %% {r}
"""
print(0)
# import os
# print(0, file=open(os.path.expanduser('~/__debug.txt'), 'a', encoding='utf-8'))
"""

# %%
print(2)


# %%
"""
# Header

@{echo=False}
```py
print(0)
```
"""

# %% {echo=False}
"""print(0)"""

# %%
"""
print(0)
"""

# %%

"""
print(111)
"""

# %%


"""
print(111)
"""



# %% {r}
""" """

# %% {r}
""""""

# %%
"""
"""

# %%
"""
print(0)
'''

# %%
print(1)
