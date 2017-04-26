# Docstring Writer
A docstring writer for Python files written in Python.

## What?
It automatically generates docstrings for functions and classes in Python
scripts.

## How?
Using the AST, it finds the arguments, attributes, returned/yielded variables
and raised exceptions and formats them, mostly following the
[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html).

## Can it replace me as the human?
No, because you still have to write descriptions that describe what the
functions do. Good documentation shows not only what variables are being used
but how and why they are being used as well.

## Can you give an example?
Yes.

## ...Give me an example.
**Running it:**

`$ python3 doc_writer.py boop.py stuff.txt`

**Input:**

*boop.py*
```python
class boop(object):
    def __init__(stuff):
        self.stuff = stuff

    def braaaap(green: bool, eggs = 'and ham', answer = 42):
        if green:
            return eggs

        if answer != 42:
            raise Exception # The answer is always 42.

# Too many references?

def aaa(aaaa, aaaaa = 'aaaaa'):
    aaaaaa = 'aaaaaa'
    return aaaaaa
```

**Output:**

*stuff.txt*
```
Docstrings for boop.py
================================================================================
boop(stuff):

"""<class description>

Initializer arguments:
    stuff (<type>): <description>

Attributes:
    stuff (<type>): <description>
"""
--------------------------------------------------------------------------------
boop.__init__(stuff):

"""See class docstring for details."""
--------------------------------------------------------------------------------
boop.braaaap(green, eggs, answer):

"""<function description>

Arguments:
    green (bool): <description>
    eggs (<type>): <description>
    answer (<type>): <description>

Returns:
    eggs (<type>): <description>

Raises:
    Exception: <description>
"""
================================================================================
aaa(aaaa, aaaaa):

"""<function description>

Arguments:
    aaaa (<type>): <description>
    aaaaa (<type>): <description>

Returns:
    aaaaaa (<type>): <description>
"""
--------------------------------------------------------------------------------
```
