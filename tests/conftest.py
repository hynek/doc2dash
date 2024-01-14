# SPDX-FileCopyrightText: 2012 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

from pathlib import Path

import pytest


@pytest.fixture(name="sphinx_docs", scope="session")
def _sphinx_docs():
    return (
        Path("tests") / "parsers" / "intersphinx" / "example-sphinx-docs"
    ).resolve()


@pytest.fixture(name="sphinx_built", scope="session")
def _sphinx_built(sphinx_docs):
    return sphinx_docs / "built_docs" / "html"
