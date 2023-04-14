#!/usr/bin/env python
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: © 2021 Massachusetts Institute of Technology.
# SPDX-FileCopyrightText: © 2021 Lee McCuller <mcculler@caltech.edu>
# NOTICE: authors should document their contributions in concisely in NOTICE
# with details inline in source files, comments, and docstrings.
"""
"""
import os
import re
import sys
import argparse
from wield.pytest.parse_collection.parse import pytest_collection_parse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description = 'Module to create a report structure for pytest collection outputs'
    )
    parser.add_argument('fname', help='collection output file name')
    parser.add_argument('test', nargs='?', help='Test name')

    #args = parser.parse_args(sys.argv[1:])
    args = parser.parse_args()

    b = pytest_collection_parse(args.fname)
    if args.test is None:
        for mod in b.tests:
            print(mod)
    else:
        print(b.tests[args.test])
