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

from shutil import rmtree
import contextlib

import sys
import pytest

from . import utilities


@pytest.fixture
def plot(request):
    return request.config.getvalue("--plot")
    return request.config.option.plot


@pytest.fixture
def tpath_preclear(request):
    """
    Fixture that indicates that the test path should be cleared automatically
    before running each test. This cleans up the test data.
    """
    tpath_root, tpath_local = utilities.tpath_root_make(request)
    no_preclear = request.config.getvalue("--no-preclear")
    if not no_preclear:
        rmtree(tpath_root, ignore_errors=True)
    return


@pytest.fixture
def tpath(request):
    """
    Fixture that takes the value of the special test-specific folder for test
    run data and plots. Usually the <folder of the test>/tresults/test_name/
    """
    tpath_root, tpath_local = utilities.tpath_root_make(request)

    os.makedirs(tpath_root, exist_ok=True)
    os.utime(tpath_root, None)

    tpath_rel = os.path.relpath(os.path.realpath(tpath_root), os.path.realpath(os.path.split(tpath_local)[0]))
    if os.path.islink(tpath_local):
        if os.path.normpath(
            os.path.join(os.path.split(tpath_local)[0], os.readlink(tpath_local))
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

    return tpath_root


def tpath_join(request):
    """
    Fixture that joins subpaths to the value of the special test-specific folder for test
    run data and plots. Usually the <folder of the test>/tresults/test_name/.

    This function should be use like test_thing.save(tpath_join('output_file.png'))
    """
    tpath_root, tpath_local = utilities.tpath_root_make(request)
    first_call = True

    def tpath_joiner(*subpath):
        nonlocal first_call
        if first_call:
            os.makedirs(tpath_root, exist_ok=True)
            os.utime(tpath_root, None)
            first_call = False

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

    return tpath_joiner


tpath_join_ = tpath_join
# make it into a fixture
tpath_join = pytest.fixture(tpath_join)


@pytest.fixture
def fpath(request):
    """
    py.test fixture that returns the folder path of the test being run. Useful
    for accessing data files.
    """
    return utilities.fpath_raw_make(request)


@pytest.fixture
def fpath_join(request):
    """
    py.test fixture that runs os.path.join(path, *arguments) to merge subpaths
    with the folder path of the current test being run. Useful for referring to
    data files.
    """

    def join_func(*path):
        return os.path.join(utilities.fpath_raw_make(request), *path)

    return join_func


@pytest.fixture(scope="function")
def closefigs():
    import matplotlib.pyplot as plt
    yield
    plt.close("all")


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
                    call(fail=did_fail, **kwargs)
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
    print("---------------:{}:--------------".format(request.node.name))

    import builtins

    builtins.dprint = utilities.dprint
    yield utilities.dprint
    return


# variable that stores the current node and capture filename information
_node_capture = None


@pytest.fixture
def capture(request):
    """ Fixture that stores the output into tpath_join('capture.txt').

    This must coordinate with pytest_runtest_logreport to function. It passes
    required information.
    """

    ### This is a previous implementation
    # in principle, this could check of the "-s"
    # command line option was used, and fall back to
    # this method if so
    # the new method is compatible with the html plugin

    #stdout = sys.stdout
    #stderr = sys.stderr

    #fname = tpath_join("capture.txt")
    #with open(fname, "w") as F:

    #    class TeeOut(object):
    #        """
    #        """
    #        def write(self, data):
    #            F.write(data)
    #            stdout.write(data)

    #        def writelines(self, lines):
    #            F.writelines(lines)
    #            stdout.writelines(lines)

    #        def flush(self):
    #            self.file.flush()
    #            stdout.flush()

    #        def isatty(self):
    #            return stdout.isatty()

    #        def fileno(self):
    #            return stdout.fileno()

    #        def __getattr__(self, name):
    #            # grab all to fix pdb issues
    #            return getattr(stdout, name)

    #    class TeeErr(object):
    #        def write(self, data):
    #            F.write("\nSTDERR: ".join(data.split("\n")))
    #            stderr.write(data)

    #        def writelines(self, lines):
    #            F.writelines(["STDERR: " + d for d in lines])
    #            stderr.writelines(lines)

    #        def flush(self):
    #            self.file.flush()
    #            stderr.flush()

    #    sys.stdout = TeeOut()
    #    sys.stderr = TeeErr()
    #    yield
    #    sys.stdout = stdout
    #    sys.stderr = stderr
    yield
    global _node_capture
    # funny notation on tpath_join_ is because it is designed to be a fixture
    _node_capture = request.node.nodeid, tpath_join_(request)("capture.txt")
    return


@contextlib.contextmanager
def ws_tracemalloc_impl():
    # TODO, this should possibly go in a separate fixture with a wider scope
    import tracemalloc
    tracemalloc.start()
    yield

    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')

    print("[ Top 10 ]")
    for stat in top_stats[:10]:
        print(stat)

@pytest.fixture()
def ws_tracemalloc():
    """
    Prints the 10 largest memory consumers at the end of each test.

    NOTE: this is an autouse fixture, so if it is imported, all of the tests in a module will use it. This
    is convenient for debugging.
    
    It is useful for debugging memory leaks that break the test suite. Often they can come from Matplotlib.
    """
    with ws_tracemalloc_impl():
        yield

@pytest.fixture(autouse=True)
def ws_tracemalloc_auto():
    """
    Prints the 10 largest memory consumers at the end of each test.

    NOTE: this is an autouse fixture, so if it is imported, all of the tests in a module will use it. This
    is convenient for debugging.
    """
    with ws_tracemalloc_impl():
        yield
