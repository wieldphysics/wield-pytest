#!/usr/bin/env python
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: © 2021 Massachusetts Institute of Technology.
# SPDX-FileCopyrightText: © 2021 Lee McCuller <mcculler@mit.edu>
# NOTICE: authors should document their contributions in concisely in NOTICE
# with details inline in source files, comments, and docstrings.
"""
"""
import time
import pytest
from os import path

try:
    import icecream
except ImportError:
    icecream = None
    pass

try:
    from IPython.lib.pretty import pretty

    pformat = pretty
except ImportError:
    from pprint import pformat


def relfile(_file_, *args, fname=None):
    fpath = path.split(_file_)[0]
    post = path.join(*args)
    fpath = path.join(fpath, post)
    # os.makedirs(fpath, exist_ok = True)
    # os.utime(fpath, None)

    if fname is None:
        return fpath
    else:
        return path.join(fpath, fname)


def relfile_root(_file_, request, pre=None, post=None):
    """
    Generates a folder specific to py.test function
    (provided by using the "request" fixture in the test's arguments)
    """
    if isinstance(pre, (list, tuple)):
        pre = path.join(pre)

    fpath, fname = path.split(_file_)
    testname = path.join(fname, request.node.name)
    if pre is not None:
        testname = path.join(pre, testname)

    if isinstance(post, (list, tuple)):
        post = path.join(post)

    if post is not None:
        return path.join(request.config.rootpath, testname, post)
    else:
        return path.join(request.config.rootpath, testname)


def relfile_test(_file_, request, pre=None, post=None, fname=None):
    """
    Generates a folder specific to py.test function
    (provided by using the "request" fixture in the test's arguments)
    """
    if isinstance(pre, (list, tuple)):
        pre = path.join(pre)

    testname = request.node.name
    if pre is not None:
        testname = path.join(pre, testname)

    if isinstance(post, (list, tuple)):
        post = path.join(post)
    if post is not None:
        return relfile(_file_, testname, post, fname=fname)
    else:
        return relfile(_file_, testname, fname=fname)


class Timer(object):
    def __init__(self, N=1):
        self.N = N

    def __iter__(self):
        return iter(range(self.N))

    def __call__(self):
        return self.interval / self.N

    def __float__(self):
        return self.interval / self.N

    def __str__(self):
        time = self()
        if time > 10:
            return "{:.1f}s".format(time)
        elif time > 1:
            return "{:.2f}s".format(time)
        elif time > .001:
            return "{:.1f}ms".format(time * 1e3)
        elif time > 1e-6:
            return "{:.1f}us".format(time * 1e6)
        else:
            return "{:.1f}ns".format(time * 1e9)

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.end = time.time()
        self.interval = self.end - self.start


def dprint(*args, F=None, pretty=True, **kwargs):
    outs = []
    if pretty:
        for arg in args:
            outs.append(pformat(arg))
    else:
        outs = args

    if icecream is not None:
        icecream.DEFAULT_OUTPUT_FUNCTION(" ".join(outs), **kwargs)
    else:
        print(*outs, **kwargs)


def tpath_root_make(
    request,
    root_folder="test_results",
    local_folder="test_results",
):
    if isinstance(request.node, pytest.Function):
        tpath_root = relfile_root(
            request.node.function.__code__.co_filename, request, pre=root_folder
        )
        tpath_local = relfile_test(
            request.node.function.__code__.co_filename, request, pre=local_folder
        )
        return tpath_root, tpath_local
    raise RuntimeError("tpath currently only works for functions")


def fpath_raw_make(request):
    if isinstance(request.node, pytest.Function):
        return path.split(request.node.function.__code__.co_filename)[0]
    raise RuntimeError("fpath currently only works for functions")
