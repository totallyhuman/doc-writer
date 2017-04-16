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

def search(n):
    for i in n.body:
        if isinstance(i, ast.FunctionDef):
            function_name = i.name
            function_args = [arg.arg for arg in i.args.args]
            function_returns = []
            function_raises = []

            for j in i.body:
                if isinstance(j, ast.Return):
                    try:
                        function_returns.append(j.value.id)
                    except AttributeError:
                        function_returns += [elts.id for elts in j.value.elts]
                if isinstance(j, ast.Raise):
                    function_raises.append(j.exc.id)

            functions.append({'name': function_name, 'args': function_args,
                              'returns': function_returns,
                              'raises': function_raises})
        else:
            try:
                search(i)
            except AttributeError:
                pass

with open(script) as f:
    node = ast.parse(f.read())
    search(node)

for f in functions:
    doc = '{}('.format(f['name'])

    if len(f['args']) > 0:
        for arg in f['args']:
            doc += arg + ', '
        doc = doc[:-2]

    doc += '):\n\n<function description>\n'

    if len(f['args']) > 0:
        doc += '\nPositional arguments:\n'
        for arg in f['args']:
            doc += '    *{} -- <argument type and description>\n'.format(arg)

    if len(f['returns']) > 0:
        doc += '\nReturns:\n'
        for var in f['returns']:
            doc += '    *{} -- <variable type and description>\n'.format(var)

    if len(f['raises']) > 0:
        doc += '\nRaises:\n'
        for exc in f['raises']:
            doc += '    *{} -- <exception description>\n'.format(exc)
        doc = doc[:-1]

    f['doc'] = doc
