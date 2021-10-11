#!/usr/bin/env python
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: © 2021 Massachusetts Institute of Technology.
# SPDX-FileCopyrightText: © 2021 Lee McCuller <mcculler@mit.edu>
# NOTICE: authors should document their contributions in concisely in NOTICE
# with details inline in source files, comments, and docstrings.
""" pytest modules for use with wavestate packages and dependent software
"""
import os
from os import path

from shutil import rmtree
import contextlib

import sys
import pytest
import subprocess

from . import utilities
from .utilities import Timer  # noqa
from ._version import version, __version__, version_info


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
        dest = 'plot',
        help = "Have tests update plots (it is slow)",
    )

    parser.addoption(
        "--no-preclear",
        action="store_true",
        default=False,
        dest='no_preclear',
        help="Do not preclear tpaths",
    )


@pytest.fixture
def plot(request):
    return request.config.getvalue('--plot')
    return request.config.option.plot


@pytest.fixture
def tpath_preclear(request):
    """
    Fixture that indicates that the test path should be cleared automatically
    before running each test. This cleans up the test data.
    """
    tpath_root, tpath_local = tpath_root_make(request)
    no_preclear = request.config.getvalue('--no-preclear')
    if not no_preclear:
        rmtree(tpath_root, ignore_errors = True)
    return


@pytest.fixture
def tpath(request):
    """
    Fixture that takes the value of the special test-specific folder for test
    run data and plots. Usually the <folder of the test>/tresults/test_name/
    """
    tpath_root, tpath_local = tpath_root_make(request, root_folder = 'test_results', local_folder = 'test_results')

    os.makedirs(tpath_root, exist_ok = True)
    os.utime(tpath_root, None)

    tpath_rel = os.path.relpath(tpath_root, os.path.split(tpath_local)[0])
    if os.path.islink(tpath_local):
        if os.path.normpath(os.path.join(os.path.split(tpath_local)[0], os.readlink(tpath_local))) != os.path.normpath(tpath_root):
            os.unlink(tpath_local)
            os.makedirs(path.split(tpath_local)[0], exist_ok = True)
            os.symlink(tpath_rel, tpath_local, target_is_directory = True)
    elif not os.path.exists(tpath_local):
        os.makedirs(path.split(tpath_local)[0], exist_ok = True)
        os.symlink(tpath_rel, tpath_local, target_is_directory = True)
    else:
        import warnings
        warnings.warn('test_results local path {} exists'.format(tpath_local))

    return tpath_root


@pytest.fixture
def tpath_join(request):
    """
    Fixture that joins subpaths to the value of the special test-specific folder for test
    run data and plots. Usually the <folder of the test>/tresults/test_name/.

    This function should be use like test_thing.save(tpath_join('output_file.png'))
    """
    tpath_root, tpath_local = tpath_root_make(request, root_folder = 'test_results', local_folder = 'test_results')
    first_call = True

    def tpath_joiner(*subpath):
        nonlocal first_call
        if first_call:
            os.makedirs(tpath_root, exist_ok = True)
            os.utime(tpath_root, None)
            first_call = False

            tpath_rel = os.path.relpath(tpath_root, os.path.split(tpath_local)[0])
            if os.path.islink(tpath_local):
                if os.path.normpath(os.path.join(os.path.split(tpath_local)[0], os.readlink(tpath_local))) != os.path.normpath(tpath_root):
                    os.unlink(tpath_local)
                    os.makedirs(path.split(tpath_local)[0], exist_ok = True)
                    os.symlink(tpath_rel, tpath_local, target_is_directory = True)
            elif not os.path.exists(tpath_local):
                os.makedirs(path.split(tpath_local)[0], exist_ok = True)
                os.symlink(tpath_rel, tpath_local, target_is_directory = True)
            else:
                import warnings
                warnings.warn('test_results local path {} exists'.format(tpath_local))
        return path.join(tpath_root, *subpath)

    return tpath_joiner


@pytest.fixture
def fpath(request):
    """
    py.test fixture that returns the folder path of the test being run. Useful
    for accessing data files.
    """
    return fpath_raw_make(request)


@pytest.fixture
def fpath_join(request):
    """
    py.test fixture that runs os.path.join(path, *arguments) to merge subpaths
    with the folder path of the current test being run. Useful for referring to
    data files.
    """
    def join_func(*path):
        return os.path.join(fpath_raw_make(request), *path)
    return join_func

@pytest.fixture
def closefigs():
    import matplotlib.pyplot as plt
    yield
    plt.close('all')


@pytest.fixture
def test_trigger():
    """
    This fixture provides a contextmanager that causes a function to call
    if an AssertionError is raised. It will also call if any of its argument,
    or keyword arguments evaluates to True. This allows you to conveniently force
    calling using other flags or fixtures.

    The primary usage of this is to plot outputs only on test failures, while also
    allowing plotting to happen using the plot fixture and pytest cmdline argument
    """
    run_store = []

    @contextlib.contextmanager
    def fail(call, **kwargs):
        run_store.append(call)

        def call(did_fail):
            do_call = did_fail
            for k, v in kwargs.items():
                if v:
                    do_call = True
                    break

            if do_call:
                for call in run_store:
                    call(fail = did_fail, **kwargs)
                run_store.clear()
        try:
            yield
        except AssertionError:
            call(True)
            raise
        else:
            call(False)

        return
    return fail


@pytest.fixture
def dprint(request, tpath_join):
    """
    This is a fixture providing a wrapper function for pretty printing. It uses
    the icecream module for pretty printing, falling back to ipythons pretty
    printer if needed, then to the python build in pretty printing module.

    Along with printing to stdout, this function prints into the tpath_folder to
    save all output into output.txt.
    """
    # pushes past the dot
    print('---------------:{}:--------------'.format(request.node.name))

    import builtins
    builtins.dprint = utilities.dprint
    yield utilities.dprint
    return


@pytest.fixture
def capture(tpath_join):
    """ Fixture that tee's stdout and stderr from python to write into the test folder.

    pytest already includes some of this functionality via its --capture line and
    capsys builtin fixtures. Users often want both real time printing of output
    with the pytest `-s` as well as capturing output into tpath test folders.
    This function provides both, but does not capture stdout or stderr from
    subprocesses or any direct file IO.

    If imported and used, tpath_join must also be imported and used.
    """
    stdout = sys.stdout
    stderr = sys.stderr

    fname = tpath_join('capture.txt')
    with open(fname, 'w') as F:
        class TeeOut(object):
            def write(self, data):
                F.write(data)
                stdout.write(data)

            def writelines(self, lines):
                F.writelines(lines)
                stdout.writelines(lines)

            def flush(self):
                self.file.flush()
                stdout.flush()

        class TeeErr(object):
            def write(self, data):
                F.write('\nSTDERR: '.join(data.split('\n')))
                stderr.write(data)

            def writelines(self, lines):
                F.writelines(['STDERR: ' + d for d in lines])
                stderr.writelines(lines)

            def flush(self):
                self.file.flush()
                stderr.flush()

        sys.stdout = TeeOut()
        sys.stderr = TeeErr()
        yield
        sys.stdout = stdout
        sys.stderr = stderr


def tpath_root_make(request, root_folder, local_folder):
    if isinstance(request.node, pytest.Function):
        tpath_root = utilities.relfile_root(request.node.function.__code__.co_filename, request, pre = root_folder)
        tpath_local = utilities.relfile_test(request.node.function.__code__.co_filename, request, pre = local_folder)
        return tpath_root, tpath_local
    raise RuntimeError("tpath currently only works for functions")


def fpath_raw_make(request):
    if isinstance(request.node, pytest.Function):
        return os.path.split(request.node.function.__code__.co_filename)[0]
    raise RuntimeError("fpath currently only works for functions")


__all__ = [
    'version',
    '__version__',
    'version_info',
    'pytest_addoption',
    'plot',
    'tpath',
    'tpath_join',
    'fpath',
    'fpath_join',
    'tpath_preclear',
    'closefigs',
    'test_trigger',
    'dprint',
    'capture',
    'tpath_root_make',
    'fpath_raw_make',
]
