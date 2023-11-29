#!/usr/bin/env python
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: © 2021 Massachusetts Institute of Technology.
# SPDX-FileCopyrightText: © 2021 Lee McCuller <mcculler@caltech.edu>
# NOTICE: authors should document their contributions in concisely in NOTICE
# with details inline in source files, comments, and docstrings.
""" pytest modules for use with wield packages and dependent software
"""
import os
from os import path

from . import utilities
from . import fixtures


def tjoin(*subpath):
    """
    function that joins subpaths to the value of the special test-specific folder for test
    run data and plots. Usually created at the pytest.ini root folder and linked to
    the <folder of the test>/tresults/test_name/.

    This function should be use like test_thing.save(tjoin('output_file.png'))
    """
    if not fixtures._pytest_request:
        raise RuntimeError("tjoin must be used from within a pytest")

    request = fixtures._pytest_request[-1]
    tpath_root, tpath_local = utilities.tpath_root_make(request)
    try:
        first_call = getattr(request, '_first_call', True)
    except AttributeError:
        first_call = True

    if first_call:
        os.makedirs(tpath_root, exist_ok=True)
        os.utime(tpath_root, None)
        first_call = False
        if request is not None:
            request._first_call = False

        tpath_rel = os.path.relpath(os.path.realpath(tpath_root), os.path.realpath(os.path.split(tpath_local)[0]))
        if os.path.islink(tpath_local):
            if os.path.normpath(
                os.path.join(
                    os.path.split(tpath_local)[0], os.readlink(tpath_local)
                )
            ) != os.path.normpath(tpath_root):
                os.unlink(tpath_local)
                os.makedirs(path.split(tpath_local)[0], exist_ok=True)
                os.symlink(tpath_rel, tpath_local, target_is_directory=True)
        elif not os.path.exists(tpath_local):
            os.makedirs(path.split(tpath_local)[0], exist_ok=True)
            os.symlink(tpath_rel, tpath_local, target_is_directory=True)
        else:
            import warnings

            warnings.warn("test_results local path {} exists".format(tpath_local))
    return path.join(tpath_root, *subpath)


def fjoin(*path):
    """
    py.test fixture that runs os.path.join(path, *arguments) to merge subpaths
    with the folder path of the current test being run. Useful for referring to
    data files.
    """

    if not fixtures._pytest_request:
        raise RuntimeError("fjoin must be used from within a pytest")

    request = fixtures._pytest_request[-1]
    return os.path.join(utilities.fpath_raw_make(request), *path)


dprint = utilities.dprint
