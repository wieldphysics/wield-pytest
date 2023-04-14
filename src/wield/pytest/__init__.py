#!/usr/bin/env python
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: © 2021 Massachusetts Institute of Technology.
# SPDX-FileCopyrightText: © 2021 Lee McCuller <mcculler@caltech.edu>
# NOTICE: authors should document their contributions in concisely in NOTICE
# with details inline in source files, comments, and docstrings.
""" pytest modules for use with wield packages and dependent software
"""

from ._version import version, __version__, version_info
from .utilities import Timer
import contextlib
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


_options_added = {}


def pytest_addoption(parser, **kwargs):
    # ensure that if this is run multiple times in conftest.py at
    # varying levels, that it doesn't conflict
    global _options_added

    if not _options_added.get('plot', False):
        parser.addoption(
            "--plot",
            action="store_true",
            dest="plot",
            help="Have tests update plots (it is slow)",
        )
        _options_added['plot'] = True

    if not _options_added.get('ws-mpl-backend', False):
        parser.addoption(
            "--ws-no-mpl-agg",
            action="store_false",
            dest="ws_mpl_backend",
            help="Don't assign agg as matplotlib backend",
        )
        _options_added['ws-mpl-backend'] = True

    if not _options_added.get('no-preclear', False):
        parser.addoption(
            "--no-preclear",
            action="store_true",
            default=False,
            dest="no_preclear",
            help="Do not preclear tpaths",
        )
        _options_added['no-preclear'] = True

    for k, call in kwargs.items():
        if not _options_added.get(k, False):
            call()
            _options_added[k] = True


def pytest_configure(config):
    if config.option.ws_mpl_backend:
        import matplotlib
        matplotlib.use('agg')


@contextlib.contextmanager
def importskip(reason=None):
    try:
        yield
    except ImportError as E:
        import pytest
        if reason is None:
            pytest.skip(allow_module_level=True, reason=str(E))
        else:
            pytest.skip(allow_module_level=True, reason=reason)


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
    "importskip",
]
