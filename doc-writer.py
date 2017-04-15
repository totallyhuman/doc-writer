#!/usr/bin/env python3
# -*- coding: utf -8 -*-

import sys

try:
    script = sys.argv[1]
except IndexError:
    print('Usage: doc-writer.py [filename]')
