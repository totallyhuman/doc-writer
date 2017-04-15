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

with open(script) as f:
    node = ast.parse(f.read())
    for i in node.body:
        if isinstance(i, ast.FunctionDef):
            function_name = i.name
            function_args = [arg.arg for arg in i.args.args]

            functions.append({'name': function_name, 'args': function_args})
