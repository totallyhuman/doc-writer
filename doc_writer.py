#!/usr/bin/env python3
# -*- coding: utf -8 -*-

from argparse import *
import ast


def find_classes(module):
    class_nodes = [c for c in ast.walk(module) if isinstance(c, ast.ClassDef)]

    return class_nodes


def find_functions(node, class_info = False):
    function_nodes = []

    if class_info:
        for f in ast.walk(node):
            if isinstance(f, ast.FunctionDef):
                function = {}

                function['node'] = f
                function['class_name'] =  node.name

                function_nodes.append(function)
    else:
        function_nodes = [f for f in ast.walk(node) if
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


def find_yield_vars(func):
    yields = []

    for j in ast.walk(func):
        if isinstance(j, ast.Yield):
            try:
                yields.append(j.value.id)
            except AttributeError:
                try:
                    yields += [elts.id for elts in j.value.elts]
                except AttributeError:
                    pass

    return yields


def find_raised_exceptions(func):
    raises = []

    for j in ast.walk(func):
        if isinstance(j, ast.Raise):
            raises.append(j.exc.id)

    return raises


def parse_functions(class_function_nodes, function_nodes):
    class_functions = []
    functions = []

    for node in class_function_nodes:
        function = {}

        function['class_name'] = node['class_name']
        function['name'] = node['node'].name
        function['args'] = [arg.arg for arg in node['node'].args.args]

        if len(function['args']) and function['args'][0] == 'self':
            function['args'].pop(0)

        function['returns'] = find_return_vars(node['node'])
        function['yields'] = find_yield_vars(node['node'])
        function['raises'] = find_raised_exceptions(node['node'])

        if function['name'] != '__init__':
            class_functions.append(function)
        else:
            function['doc'] = 'See class docstring for details.\n'

    for node in function_nodes:
        function = {}

        function['name'] = node.name
        function['args'] = [arg.arg for arg in node.args.args]

        if len(function['args']) and function['args'][0] == 'self':
            function['args'].pop(0)

        function['returns'] = find_return_vars(node)
        function['yields'] = find_yield_vars(node)
        function['raises'] = find_raised_exceptions(node)

        functions.append(function)
    return class_functions, functions


def parse_classes(class_nodes):
    classes = []

    for node in class_nodes:
        c = {}

        c['name'] = node.name
        for i in node.body:
            try:
                if isinstance(i, ast.FunctionDef) and i.name == '__init__':
                    c['args'] = [arg.arg for arg in i.args.args]
                    c['attr'] = []

                    for j in ast.walk(i):
                        if isinstance(j, ast.Attribute):
                            c['attr'].append(j.attr)
            except AttributeError:
                pass

        classes.append(c)

    return classes


def format_funcs(functions):
    for f in functions:
        try:
            doc_list = ['{}.'.format(f['class_name'])]
        except KeyError:
            doc_list = []

        doc_list.append('{}('.format(f['name']))

        if len(f['args']):
            for arg in f['args']:
                doc_list.append(arg + ', ')
            doc_list[-1] = doc_list[-1][:-2]

        doc_list.append('):\n\n<function description>\n')

        if len(f['args']):
            doc_list.append('\nArguments:\n')
            for arg in f['args']:
                doc_list.append('    {}: <argument type and description>\n'
                                .format(arg))

        if len(f['returns']):
            doc_list.append('\nReturns:\n')
            for var in f['returns']:
                doc_list.append('    {}: <variable type and description>\n'
                                .format(var))

        if len(f['yields']):
            doc_list.append('\nYields:\n')
            for var in f['yields']:
                doc_list.append('    {}: <variable type and description>\n'
                                .format(var))

        if len(f['raises']):
            doc_list.append('\nRaises:\n')
            for exc in f['raises']:
                doc_list.append('    {}: <exception description>\n'
                                .format(exc))

        doc_list.append('\n')

        doc = ''.join(doc_list)
        if 'doc' not in f:
            f['doc'] = doc

    return functions


def format_classes(classes):
    for c in classes:
        try:
            doc_list = ['{}('.format(c['name'])]
        except KeyError:
            doc_list = []

        if len(c['args']):
            for arg in c['args']:
                doc_list.append(arg + ', ')
            doc_list[-1] = doc_list[-1][:-2]

        doc_list.append('):\n\n<class description>\n')

        if len(c['args']):
            doc_list.append('\nArguments:\n')
            for arg in c['args']:
                doc_list.append('    {}: <argument type and description>\n'
                                .format(arg))

        if len(c['attr']):
            doc_list.append('\nAttributes:\n')
            for attr in c['attr']:
                doc_list.append('    {}: <attribute type and description\n'
                                .format(attr))

        doc_list.append('\n')

        doc = ''.join(doc_list)
        c['doc'] = doc

    return classes


def sort_docs(classes, class_functions, functions):
    docs = []

    for c in classes:
        docs.append(c['doc'])

        for f in class_functions:
            if c['name'] == f['class_name']:
                docs.append(f['doc'])

    for f in functions:
        docs.append(f['doc'])

    return docs


def main():
    parser = ArgumentParser(description = 'Generate docstrings for a Python '
                            'script.')
    parser.add_argument('filename', help = 'The name of the script to '
                        'generate docstrings for.')
    args = parser.parse_args()
    script = args.filename

    with open(script) as f:
        node = ast.parse(f.read())
        class_nodes = find_classes(node)

        all_function_nodes = []
        class_function_nodes = []

        for c in class_nodes:
            class_function_nodes += find_functions(c, class_info = True)

        all_function_nodes = find_functions(node)

        for x in class_function_nodes:
            all_function_nodes.remove(x['node'])

        class_functions, functions = parse_functions(class_function_nodes,
                                                     all_function_nodes)

        classes = parse_classes(class_nodes)

    class_functions = format_funcs(class_functions)
    functions = format_funcs(functions)
    classes = format_classes(classes)

    docs = sort_docs(classes, class_functions, functions)


if __name__ == '__main__':
    main()
