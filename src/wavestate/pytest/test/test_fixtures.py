#!/usr/bin/env python
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: © 2021 Massachusetts Institute of Technology.
# SPDX-FileCopyrightText: © 2021 Lee McCuller <mcculler@mit.edu>
# NOTICE: authors should document their contributions in concisely in NOTICE
# with details inline in source files, comments, and docstrings.
"""
"""
import sys
from wavestate.pytest import ( # noqa
    dprint, tpath_join, tpath, plot, fpath, capture
)


def test_pytest_tpath(tpath_join, fpath, dprint, capture):
    with open(tpath_join('test.txt'), 'w') as f:
        f.write('test\n')

    print('test output')
    print('test output')
    print('test output')
    print('test output')
    print('test output', file=sys.stderr)
    print('test output')
    print('test output')
    print('test output' )
    return
