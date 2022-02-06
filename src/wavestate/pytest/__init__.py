#!/usr/bin/env python
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: © 2021 Massachusetts Institute of Technology.
# SPDX-FileCopyrightText: © 2021 Lee McCuller <mcculler@mit.edu>
# NOTICE: authors should document their contributions in concisely in NOTICE
# with details inline in source files, comments, and docstrings.
""" pytest modules for use with wavestate packages and dependent software
"""

from ._version import version, __version__, version_info
from .utilities import Timer
from .fixtures import (
    plot,
    tpath,
    tpath_join,
    fpath,
    fpath_join,
    tpath_preclear,
    closefigs,
    test_trigger,
    dprint,
    capture,
)


_options_added = False


def pytest_addoption(parser):
    # ensure that if this is run multiple times in conftest.py at
    # varying levels, that it doesn't conflict
    global _options_added
    if _options_added:
        return
    else:
        _options_added = True

    parser.addoption(
        "--plot",
        action="store_true",
        dest="plot",
        help="Have tests update plots (it is slow)",
    )

    parser.addoption(
        "--no-preclear",
        action="store_true",
        default=False,
        dest="no_preclear",
        help="Do not preclear tpaths",
    )


__all__ = [
    "version",
    "__version__",
    "version_info",
    "pytest_addoption",
    "plot",
    "tpath",
    "tpath_join",
    "fpath",
    "fpath_join",
    "tpath_preclear",
    "closefigs",
    "test_trigger",
    "dprint",
    "capture",
    "tpath_root_make",
    "fpath_raw_make",
    "Timer",
]
