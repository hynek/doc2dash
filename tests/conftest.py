from pathlib import Path

import pytest


@pytest.fixture(name="sphinx_docs", scope="session")
def _sphinx_docs():
    return (
        Path("tests") / "parsers" / "intersphinx" / "example-sphinx-docs"
    ).absolute()


@pytest.fixture(name="sphinx_built", scope="session")
def _sphinx_built(sphinx_docs):
    return sphinx_docs / "built_docs" / "html"


@pytest.fixture(name="objects_inv", scope="session")
def _objects_inv(sphinx_built):
    return sphinx_built / "objects.inv"
