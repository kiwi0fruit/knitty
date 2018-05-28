# Hydrogen Atom package for Knitty

* [Install Hydrogen Atom package](#install-hydrogen-atom-package)
* [Using Hydrogen](#using-hydrogen)


# Install Hydrogen Atom package

Install [**Hydrogen**](https://atom.io/packages/hydrogen) (by *nteract*) Atom package that allows interactive python code execution.

In order to make it work you may need to specify some Hydrogen settings (**Settings** → **Packages** → **Hydrogen**):

  * Specify **Language Mappings** with **kernel**: **grammar** mappings like: `{ "ir": "r", "python": "magicpython" }`,
  * Set **Startup Code** to `{"python": "KNITTY=False"}`,
  * Register Jupyter kernels in the system so that Hydrogen can find them. First:

```sh
activate the_env
```
(`call activate the_env`/`source activate the_env` in shell scripts).

Then:

```sh
python -m ipykernel install --user --name the_env
```

(presumably names can be different in the first/second commands).


# Using Hydrogen

[Hydrogen](https://atom.io/packages/hydrogen) Atom package allows interactive python code execution:

  * `Ctrl+Enter` executes the line,
  * `Ctrl+Alt+Enter` executes the cell,
  * See more commands in `Ctrl+Shift+P` and typing `hydro`,
  * The **.py** file is split into cells by the following line comments:

```python
# %%
```

  * Or you can use markdown document (**.md**) and execute the whole code chunk like this:

````python
```python
s = 'Hello!'
print(s)
```
````
