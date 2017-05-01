#!/usr/bin/env python3
# -*- coding: utf -8 -*-

from argparse import ArgumentParser
import ast


def find_classes(module):
    class_nodes = [c for c in ast.walk(module) if isinstance(c, ast.ClassDef)]

    return class_nodes


def find_functions(body, class_info = False):
    function_nodes = []

    if class_info:
        for node in ast.walk(body):
            if isinstance(node, ast.FunctionDef):
                function = {}

                function['node'] = node
                function['class_name'] = body.name

                function_nodes.append(function)
    else:
        function_nodes = [
            node for node in ast.walk(body)
            if isinstance(node, ast.FunctionDef)
        ]

    return function_nodes


def find_args(func):
    args = []

    for arg in func.args.args:
        argument = {}
        argument['name'] = arg.arg

        try:
            argument['type'] = arg.annotation.id
        except AttributeError:
            pass

        args.append(argument)

    if len(args) and (args[0]['name'] == 'self' or args[0]['name'] == 'cls'):
        args.pop(0)

    return args


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
        function['lineno'] = node['node'].lineno
        function['args'] = find_args(node['node'])
        function['returns'] = find_return_vars(node['node'])
        function['yields'] = find_yield_vars(node['node'])
        function['raises'] = find_raised_exceptions(node['node'])

        if function['name'] == '__init__':
            args = ', '.join([arg['name'] for arg in function['args']])
            function['doc'] = ('{0}.__init__({1}) at line {2}:\n\n"""See class'
                               ' docstring for details."""\n'.format(
                                   function['class_name'], args,
                                   node['node'].lineno))

        class_functions.append(function)

    for node in function_nodes:
        function = {}

        function['name'] = node.name
        function['lineno'] = node.lineno
        function['args'] = find_args(node)
        function['returns'] = find_return_vars(node)
        function['yields'] = find_yield_vars(node)
        function['raises'] = find_raised_exceptions(node)

        functions.append(function)

    return class_functions, functions


def parse_classes(class_nodes):
    classes = []

    for node in class_nodes:
        class_ = {}

        class_['name'] = node.name
        class_['lineno'] = node.lineno
        class_['args'] = []
        class_['attr'] = []

        for i in node.body:
            try:
                if isinstance(i, ast.FunctionDef) and i.name == '__init__':
                    for arg in i.args.args:
                        argument = {}
                        argument['name'] = arg.arg

                        try:
                            argument['type'] = arg.annotation.id
                        except AttributeError:
                            pass

                        class_['args'].append(argument)

                    if len(class_['args']) and (
                            class_['args'][0]['name'] == 'self' or
                            class_['args'][0]['name'] == 'cls'):
                        class_['args'].pop(0)

                    class_['attr'] = []

                    for j in ast.walk(i):
                        if isinstance(j, ast.Attribute):
                            class_['attr'].append(j.attr)
            except AttributeError:
                pass

        classes.append(class_)

    return classes


def format_funcs(functions):
    for func in functions:
        try:
            doc_list = ['{}.'.format(func['class_name'])]
        except KeyError:
            doc_list = []

        doc_list.append('{}('.format(func['name']))

        if len(func['args']):
            for arg in func['args']:
                doc_list.append(arg['name'] + ', ')
            doc_list[-1] = doc_list[-1][:-2]

        doc_list.append(') at line {}:\n\n"""<function description>'
                        .format(func['lineno']))

        if any([
                len(func['args']), len(func['returns']), len(func['yields']),
                len(func['raises'])
        ]):
            doc_list.append('\n')

            if len(func['args']):
                doc_list.append('\nArguments:\n')
                for arg in func['args']:
                    try:
                        doc_list.append('    {0} ({1}): <description>\n'.format(
                            arg['name'], arg['type']))
                    except KeyError:
                        doc_list.append('    {0} ({1}): <description>\n'.format(
                            arg['name'], '<type>'))

            if len(func['returns']):
                doc_list.append('\nReturns:\n')
                for var in func['returns']:
                    doc_list.append('    {} (<type>): <description>\n'
                                    .format(var))

            if len(func['yields']):
                doc_list.append('\nYields:\n')
                for var in func['yields']:
                    doc_list.append('    {} (<type>): <description>\n'
                                    .format(var))

            if len(func['raises']):
                doc_list.append('\nRaises:\n')
                for exc in func['raises']:
                    doc_list.append('    {}: <description>\n'
                                    .format(exc))

        doc_list.append('"""\n')

        doc = ''.join(doc_list)
        if 'doc' not in func:
            func['doc'] = doc

    return functions


def format_classes(classes):
    for class_ in classes:
        try:
            doc_list = ['{}('.format(class_['name'])]
        except KeyError:
            doc_list = []

        if len(class_['args']):
            for arg in class_['args']:
                doc_list.append(arg['name'] + ', ')
            doc_list[-1] = doc_list[-1][:-2]

        doc_list.append(') at line {}:\n\n"""<class description>'
                        .format(class_['lineno']))

        if any([len(class_['args']), len(class_['attr'])]):
            doc_list.append('\n')

            if len(class_['args']):
                doc_list.append('\nInitializer arguments:\n')
                for arg in class_['args']:
                    try:
                        doc_list.append('    {0} ({1}): <description>\n'.format(
                            arg['name'], arg['type']))
                    except KeyError:
                        doc_list.append('    {0} ({1}): <description>\n'.format(
                            arg['name'], '<type>'))

            if len(class_['attr']):
                doc_list.append('\nAttributes:\n')
                for attr in class_['attr']:
                    doc_list.append('    {} (<type>): <description>\n'
                                    .format(attr))

        doc_list.append('"""\n')

        doc = ''.join(doc_list)
        class_['doc'] = doc

    return classes


def sort_docs(classes, class_functions, functions):
    doc_list = []

    for class_ in classes:
        doc_list.append(class_['doc'])

        for class_function in class_functions:
            if class_['name'] == class_function['class_name']:
                doc_list.append('-' * 80 + '\n')
                doc_list.append(class_function['doc'])

        doc_list.append('=' * 80 + '\n')

    for func in functions:
        doc_list.append(func['doc'])
        doc_list.append('-' * 80 + '\n')

    docs = ''.join(doc_list)
    return docs


def main():
    parser = ArgumentParser(description = 'Generate docstrings for a Python '
                            'script. Writes output to a specified text file.')
    parser.add_argument(
        'input_file',
        help = 'The name of the Python script to generate docstrings for.')
    parser.add_argument(
        'output_file',
        help = 'The name of the file to write the docstrings to.')

    args = parser.parse_args()

    py_extensions = ('.py', '.py3', '.pyw')

    if not args.input_file.endswith(py_extensions):
        print('Input file must be a python script.')
        return

    if not args.output_file.endswith('.txt'):
        print('Output file must be a valid text file.')
        return

    script = args.input_file
    output = args.output_file

    with open(script) as input_file:
        node = ast.parse(input_file.read())

    class_nodes = find_classes(node)

    all_function_nodes = []
    class_function_nodes = []

    for class_node in class_nodes:
        class_function_nodes += find_functions(class_node, class_info = True)

    all_function_nodes = find_functions(node)

    for class_function_node in class_function_nodes:
        all_function_nodes.remove(class_function_node['node'])

    class_functions, functions = parse_functions(class_function_nodes,
                                                 all_function_nodes)

    classes = parse_classes(class_nodes)

    class_functions = format_funcs(class_functions)
    functions = format_funcs(functions)
    classes = format_classes(classes)

    docs = sort_docs(classes, class_functions, functions)

    with open(output, mode = 'w') as output_file:
        output_file.write('Docstrings for {}\n'.format(script))
        output_file.write('=' * 80 + '\n')
        output_file.write(docs)


if __name__ == '__main__':
    main()
