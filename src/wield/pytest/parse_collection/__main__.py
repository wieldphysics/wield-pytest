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
    parser.add_argument('--sort', action='store', default=None, help='sort file when outputting all tests (does not have to exist)')
    parser.add_argument('--api_rst', action='store_true', default=None, help='Create the autodoc API list')
    parser.add_argument('test', nargs='?', help='Test name')

    # args = parser.parse_args(sys.argv[1:])
    args = parser.parse_args()

    b = pytest_collection_parse(args.fname)
    if args.test is None:
        used_sort = False
        if args.api_rst:
            """
            This brach creates an RST file with all of the known test modules
            """
            paths = []
            for t in b.tests:
                tpath, ext = os.path.splitext(b.tests[t])

                if ext != '.py':
                    continue

                tpath = tpath.split('src/')
                tpath = tpath[-1]
                tpath = tpath.replace('/', '.')
                paths.append(tpath)

            def split(paths, N=0):
                paths.sort()
                last_spl = None
                last_arr = []
                arrs = {}
                for p in paths:
                    spl = p.split('.')[:N]
                    if spl == last_spl:
                        last_arr.append(p)
                    else:
                        last_spl = spl
                        last_arr = [p]
                        arrs[tuple(spl)] = last_arr
                arrs2 = {}
                for k, arr in arrs.items():
                    if len(arr) > 12:
                        arr2 = split(arr, N=N+1)
                        if len(arr2) < len(arr):
                            arrs2.update(arr2)
                        else:
                            arrs2[k] = arr
                    else:
                        arrs2[k] = arr
                return arrs2
            arrs = split(paths)

            for k, arr in arrs.items():
                kmod='.'.join(k)
                prefix="""
{}
{}

.. autosummary::
   :recursive:
   :template: custom-module-template.rst
   :toctree: _autosummary
""".format(kmod, '-'*(3 + len(kmod)))
                print(prefix)
                for a in arr:
                    print('   {}'.format(a))
                print()
            print()

            print("""
notebooks:
----------------------

""")
            # loop through the list of notebook paths
            for nb in sorted(b.notebooks):
                if not nb.startswith('docs/'):
                    print(" - ", ":doc:`{} <testing/{}>`".format(nb, os.path.splitext(nb)[0]))
                else:
                    nb = nb[5:]
                    print(" - ", ":doc:`{} <{}>`".format(nb, os.path.splitext(nb)[0]))
            print()
            print("""
.. toctree::
   :maxdepth:1
   :hidden:
""")
            # loop through the list of notebook paths
            for nb in sorted(b.notebooks):
                if not nb.startswith('docs/'):
                    print("   ", "testing/{}".format(os.path.splitext(nb)[0]))
                else:
                    nb = nb[5:]
                    print("   ", "{}".format(os.path.splitext(nb)[0]))
            print()
        else:
            """
            This branch prints all of the tests to run. It uses the timing sort information if given
            """
            if args.sort is not None:
                try:
                    with open(args.sort) as Fsort:
                        sorts = [line.strip() for line in Fsort.readlines()]
                    ssorts = set(sorts)
                    stests = set(b.tests)
                    for s in ssorts - stests:
                        sorts.remove(s)
                    for s in sorts:
                        print(s)
                    for s in stests - ssorts:
                        print(s)
                    used_sort = True
                except Exception:
                    pass
            if not used_sort:
                for mod in b.tests:
                    print(mod)
    else:
        print(b.tests[args.test])
