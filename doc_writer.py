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
    function_nodes = [f for f in ast.walk(module) if
                      isinstance(f, ast.FunctionDef)]
    return function_nodes


def find_return_vars(func):
    returns = []

    for j in ast.walk(func):
        if isinstance(j, ast.Return):
            try:
                returns.append(j.value.id)
            except AttributeError:
                try:
                    returns += [elts.id for elts in j.value.elts]
                except AttributeError:
                    pass

    return returns


def find_raised_exceptions(func):
    raises = []

    for j in ast.walk(func):
        if isinstance(j, ast.Raise):
            raises.append(j.exc.id)

    return raises


def parse_functions(function_nodes):
    functions = []

    for node in function_nodes:
        function = {}

        function['name'] = node.name
        function['args'] = [arg.arg for arg in node.args.args]

        if len(function['args']) and function['args'][0] == 'self':
            function['args'].pop(0)

        function['returns'] = find_return_vars(node)
        function['raises'] = find_raised_exceptions(node)

        functions.append(function)

    return functions

def main():
    with open(script) as f:
        node = ast.parse(f.read())
        function_nodes = find_functions(node)
        functions = parse_functions(function_nodes)

    for f in functions:
        doc_list = ['{}('.format(f['name'])]

        if len(f['args']) > 0:
            for arg in f['args']:
                doc_list.append(arg + ', ')
            doc_list[-1] = doc_list[-1][:-2]

        doc_list.append('):\n\n<function description>')

        if len(f['args']) > 0:
            doc_list.append('\n\nArguments:\n')
            for arg in f['args']:
                doc_list.append('    *{}: <argument type and description>\n'
                                .format(arg))

        if len(f['returns']) > 0:
            doc_list.append('\nReturns:\n')
            for var in f['returns']:
                doc_list.append('    *{}: <variable type and description>\n'
                                .format(var))

        if len(f['raises']) > 0:
            doc_list.append('\nRaises:\n')
            for exc in f['raises']:
                doc_list.append('    *{}: <exception description>\n'.format(exc))
            doc_list[-1] = doc_list[-1][:-1]

        doc = ''.join(doc_list)
        f['doc'] = doc

if __name__ == '__main__':
    main()
