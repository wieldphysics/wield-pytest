#!/usr/bin/env python
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: © 2022 California Institute of Technology.
# SPDX-FileCopyrightText: © 2021 Massachusetts Institute of Technology.
# SPDX-FileCopyrightText: © 2022 Lee McCuller <mcculler@caltech.edu>
# NOTICE: authors should document their contributions in concisely in NOTICE
# with details inline in source files, comments, and docstrings.
"""
"""
import pytest
import os
import wield.pytest
import wield.pytest.fixtures
from wield.pytest.fixtures import (  # noqa
    tpath,
    closefigs,
    capture,
)


def pytest_addoption(parser):

    def IFO():
        parser.addoption("--IFO", default="", help="IFO's to run (default:all)")

    def wield_collectonly():
        parser.addoption(
            "--wield-collect-only", "--ws-co", dest="ws_collectonly", action="store_true", default=None,
            help="Print test items in a custom format for wield"
        )

    def WS_SKIP_SLOW():
        parser.addoption("--ws-skip-slow", action="store_true", help="Skip slow tests (marked with ws_slow)")

    wield.pytest.pytest_addoption(
        parser,
        IFO=IFO,
        wield_collectonly=wield_collectonly,
        WS_SKIP_SLOW=WS_SKIP_SLOW
    )


def pytest_collection_modifyitems(config, items):
    skip_slow = pytest.mark.skip(reason="marked ws_slow and --ws-skip-slow indicated")
    if config.getoption("--ws-skip-slow"):
        for item in items:
            if "ws_slow" in item.keywords:
                item.add_marker(skip_slow)


@pytest.hookimpl()
def pytest_report_collectionfinish(config, start_path, items):
    lines = []
    if config.option.ws_collectonly is not None:
        stack = []
        indent = ""
        for item in items:
            needed_collectors = item.listchain()[1:]  # strip root node
            while stack:
                if stack == needed_collectors[: len(stack)]:
                    break
                stack.pop()
            for col in needed_collectors[len(stack) :]:
                stack.append(col)
                indent = (len(stack) - 1) * "  "
                relp = os.path.relpath(col.path, start_path)
                # TODO, find a way to avoid using print?
                # Other pytest things use the TerminalReporter
                # but it is difficult to prevent other output from collect-only
                # if trying to use that..
                print('{}{}::{}::{}'.format(indent, col.__class__.__name__, col.name, relp))
        pytest.exit('Done!')
        return lines
    else:
        return


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_logreport(report):
    """Stores captured report output by coordinating with the "capture" fixture

    """
    yield
    if report.when == 'teardown':
        # print("HOOKWRAP", report.nodeid, wield.pytest.fixtures._node_capture)
        if wield.pytest.fixtures._node_capture is not None:
            nodeid_from, location_from = wield.pytest.fixtures._node_capture
            if report.nodeid == nodeid_from:
                # text = report.longreprtext or report.full_text
                with open(location_from, "w") as F:
                    for section in report.sections:
                        header, content = section
                        F.write(header)
                        F.write(content)


def pytest_configure(config):
    """
    Setup collectonly
    """
    # run wield's as well
    from wield.pytest import pytest_configure
    pytest_configure(config)

    if config.option.ws_collectonly is not None:
        if not config.option.collectonly:
            config.option.collectonly = True
            config.option.htmlpath = ""
            pass

    config.addinivalue_line(
        "markers", "ws_slow: mark test as slow (deselect with --ws-noslow)"
    )

