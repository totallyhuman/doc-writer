#!/usr/bin/env python3
# -*- coding: utf -8 -*-

from argparse import *
import ast

parser = ArgumentParser(description = 'Generate docstrings for a Python '
                        'script.')
parser.add_argument('filename', help = 'The name of the script to generate '
                    'docstrings for.')
args = parser.parse_args()
script = args.filename

functions = []

def find_functions(module):
    function_nodes = [f for f in ast.walk(module) if isinstance(f, ast.FunctionDef)]
    return function_nodes

def find_return_vars(func):
    returns = []

    for j in ast.walk(func):
        if isinstance(j, ast.Return):
            try:
                returns.append(j.value.id)
            except AttributeError:
                returns += [elts.id for elts in j.value.elts]
            except AttributeError:
                pass

    return returns

def parse_functions(function_nodes):
    functions = []

    for node in function_nodes:
        function = {}

        function['name'] = node.name
        function['args'] = [arg.arg for arg in node.args.args]
        function['returns'] = find_return_vars(node)

        functions.append(function)

    return functions

with open(script) as f:
    node = ast.parse(f.read())
    function_nodes = find_functions(node)
    functions = parse_functions(function_nodes)

for f in functions:
    doc = '{}('.format(f['name'])

    if len(f['args']) > 0:
        for arg in f['args']:
            doc += arg + ', '
        doc = doc[:-2]

    doc += '):\n\n<function description>'

    if len(f['args']) > 0:
        doc += '\n\nPositional arguments:\n'
        for arg in f['args']:
            doc += '    *{} -- <argument type and description>\n'.format(arg)

    if len(f['returns']) > 0:
        doc += '\nReturns:\n'
        for var in f['returns']:
            doc += '    *{} -- <variable type and description>\n'.format(var)

    """
    if len(f['raises']) > 0:
        doc += '\nRaises:\n'
        for exc in f['raises']:
            doc += '    *{} -- <exception description>\n'.format(exc)
        doc = doc[:-1]
    """

    f['doc'] = doc
