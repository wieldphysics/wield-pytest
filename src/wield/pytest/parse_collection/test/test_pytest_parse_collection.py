#!/usr/bin/env python
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: © 2022 California Institute of Technology.
# SPDX-FileCopyrightText: © 2022 Lee McCuller <mcculler@caltech.edu>
# NOTICE: authors should document their contributions in concisely in NOTICE
# with details inline in source files, comments, and docstrings.
"""
"""
import subprocess

from wield.pytest.fixtures import (  # noqa
    dprint,
    tjoin,
    fjoin
)

from wield.pytest.parse_collection import pytest_collection_parse

def test_pytest_split_collection(tjoin, fjoin, dprint):

    b = pytest_collection_parse(fjoin("./collection_errors.txt"))

    dprint(b.modules)
    dprint(b.tests)


    b = pytest_collection_parse(fjoin("./collection_clean.txt"))

    dprint(b.modules)
    dprint(b.tests)
    return


def test_pytest_collection_run(tjoin, fjoin):
    print()
    out = subprocess.run(
        [
            'python3',
            '-m',
            'wield.pytest.parse_collection',
            fjoin("./collection_clean.txt")
        ],
        # capture_output = True,
    )
    try:
        out.check_returncode()
    except subprocess.CalledProcessError:
        print(out.stderr)
        raise

    print("STDOUT: ", out.stdout)

