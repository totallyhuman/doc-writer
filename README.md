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
**Input:**
```python
class boop(object):
    def __init__(stuff):
        self.stuff = stuff

    def braaaap(green, eggs_and = 'answer', ham = 42):
        if green:
            return eggs_and

        if ham != 42:
            raise Exception
```

**Output:**
```
boop(stuff):

<class description>

Arguments:
    stuff: <argument type and description>

Attributes:
    stuff: <attribute type and description>

boop.__init__(stuff):

See class docstring for details.

boop.braaaap(green, eggs_and, ham):

<function description>

Arguments:
    green: <argument type and description>
    eggs_and: <argument type and description>
    ham: <argument type and description>

Returns:
    eggs_and: <variable type and description>

Raises:
    Exception: <exception description>
```
