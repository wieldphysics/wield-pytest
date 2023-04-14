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
from wield.bunch import Bunch
import subprocess

RE_item = re.compile(r'^(\s*)(\w+)::(.*)::(.*)$')


def pytest_collection_parse(fname):
    # mapping of packages to modules
    packages = {None: []}
    # mapping of modules to tests
    modules = {}
    tests = {}

    current_package = None
    current_module = None
    last_indent = ""
    with open(fname, "r") as f:
        for line in f.readlines():
            line = line.rstrip()
            m = RE_item.match(line)
            if m:
                indent = m.group(1)
                indent_diff = len(indent) - len(last_indent)
                if indent_diff < -4:
                    current_module = None
                    current_package = None
                elif indent_diff < -2:
                    if current_module is None:
                        current_package = None
                    else:
                        current_module = None
                last_indent = indent
                itemtype = m.group(2)
                itemname = m.group(3)
                itempath = m.group(4)

                if itemtype == 'Package':
                    current_package = itemname
                    packages[current_package] = []
                elif itemtype == 'Module':
                    current_module = itemname
                    packages[current_package].append(current_module)
                    modules[current_module] = []

                    fpath, fmod = os.path.split(itemname)
                    modname, modext = os.path.splitext(fmod)
                    tests[modname] = itempath
                    pass
                elif itemtype == 'Function':
                    current_function = itemname
                    modules[current_module].append(current_function)
                else:
                    raise RuntimeError("Unrecognized Group Type")
    if current_module is None:
        raise RuntimeError("Didn't parse any modules! Did the format change?")


    return Bunch(
        packages = packages,
        modules = modules,
        tests = tests,
    )


