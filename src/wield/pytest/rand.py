#!/usr/bin/env python
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: © 2023 California Institute of Technology.
# SPDX-FileCopyrightText: © 2023 Lee McCuller <mcculler@caltech.edu>
# NOTICE: authors should document their contributions in concisely in NOTICE
# with details inline in source files, comments, and docstrings.
"""
This is a runnable module using

python -m wield.pytest.rand

and 

python -m wield.pytest.rand test_name.py

the first invocation outputs a simple 6-alphanumeric digit string. The second invocation moves the file test_name.py to test_name_A1B2C3.py.

This utility is to add unique codes to test names to help ensure that they are unique.
"""
import random
import string
import shutil
import sys
import os
import re


if __name__ == '__main__':
    def rando():
        x = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        return x

    if len(sys.argv) > 1:
        for fname in sys.argv[1:]:
            fbase, fext = os.path.splitext(fname)

            ftag = fbase[-7:]
            m = re.match('_[0-9A-Z]{6}', ftag)
            if m:
                exit(0)

            fnew = fbase + '_' + rando() + fext

            try:
                shutil.move(fname, fnew)
            except Exception as e:
                print('error moving {} to {}'.format(fname, fnew), file=sys.stderr)
                exit(1)

    else:
        print(rando())
