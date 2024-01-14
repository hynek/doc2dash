# SPDX-FileCopyrightText: 2012 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

from unittest.mock import Mock

import pytest

from doc2dash.parsers import intersphinx_inventory
from doc2dash.parsers.intersphinx_inventory import (
    CachedFileExists,
    _clean_up_path,
    _lines_to_tuples,
    load_inventory,
)


def test_parse_example(sphinx_built):
    """
    Parses our example objects.inv correctly.
    """
    entries = dict(load_inventory(sphinx_built))

    assert {
        "py:attribute": {
            "some_module.LeClass.AnAttr": (
                "index.html#some_module.LeClass.AnAttr",
                "-",
            )
        },
        "py:class": {
            "some_module.LeClass": ("index.html#some_module.LeClass", "-")
        },
        "py:data": {
            "some_module.BoringData": (
                "index.html#some_module.BoringData",
                "-",
            )
        },
        "py:function": {
            "some_module.func": ("index.html#some_module.func", "-")
        },
        "py:method": {
            "some_module.LeClass.DieMethod": (
                "index.html#some_module.LeClass.DieMethod",
                "-",
            )
        },
        "py:module": {"some_module": ("index.html#module-some_module", "-")},
        "py:property": {
            "some_module.LeClass.Mine": (
                "index.html#some_module.LeClass.Mine",
                "-",
            )
        },
        "std:cmdoption": {"--foo": ("index.html#cmdoption-foo", "-")},
        "std:doc": {
            "index": (
                "index.html",
                "Let’s define some symbols and see if doc2dash can handle "
                "them!",
            ),
            "glossary": ("glossary.html", "A Glossary"),
        },
        "std:envvar": {
            "ENV_VARIABLE": ("index.html#envvar-ENV_VARIABLE", "-")
        },
        "std:label": {
            "genindex": ("genindex.html", "Index"),
            "modindex": ("py-modindex.html", "Module Index"),
            "py-modindex": ("py-modindex.html", "Python Module Index"),
            "search": ("search.html", "Search Page"),
        },
        "std:term": {
            "Foobar": ("glossary.html#term-Foobar", "-"),
            "multi-word term": ("glossary.html#term-multi-word-term", "-"),
            "mwt": ("glossary.html#term-mwt", "-"),
        },
    } == entries


def test_missing_file(caplog):
    """
    If a file is missing, don't add it to the index.
    """
    assert {} == _lines_to_tuples(
        lambda _: False, ["name role 1 path.html#anchor -"]
    )


def test_bad_format(caplog):
    """
    If a line is malformed, warn about it and don't add it to the index.
    """
    assert {} == _lines_to_tuples(lambda _: True, ["yolo"])
    assert ["intersphinx: invalid line: 'yolo'. Skipping."] == caplog.messages


@pytest.mark.parametrize(
    "path,expected",
    [
        ("docs.html", ("docs.html", "docs.html")),
        ("docs/", ("docs/index.html", "docs/index.html")),
        ("docs.html#api", ("docs.html", "docs.html#api")),
        ("docs/#api", ("docs/index.html", "docs/index.html#api")),
        ("docs.html#foo#api", ("docs.html", "docs.html#api")),
        ("docs/#foo#api", ("docs/index.html", "docs/index.html#api")),
    ],
)
def test_cleanup_path(path, expected):
    """
    Paths without an anchor are passed through.
    """
    assert expected == _clean_up_path(path)


class TestCachedFileExists:
    def test_detects_exists_and_caches(self, tmp_path, monkeypatch):
        """
        Existing files are detected as such and their existence is cached.
        """
        cfe = CachedFileExists(tmp_path)

        (tmp_path / "exists").write_text("i exist!")

        assert cfe("exists")
        assert {"exists"} == cfe._exists
        assert set() == cfe._missing

        # Should use cache
        m = Mock()
        monkeypatch.setattr(intersphinx_inventory, "Path", m)

        assert cfe("exists")
        m.assert_not_called()

    def test_detects_missing_and_caches(self, tmp_path, monkeypatch, caplog):
        """
        Missing files are detected as such and their lack of existence is
        cached. Exactly one log warning is emitted per file.
        """
        cfe = CachedFileExists(tmp_path)

        assert not cfe("missing")
        assert set() == cfe._exists
        assert {"missing"} == cfe._missing

        # Should use cache
        m = Mock()
        monkeypatch.setattr(intersphinx_inventory, "Path", m)

        assert not cfe("missing")
        m.assert_not_called()

        assert [
            "intersphinx: path 'missing' is in objects.inv, but does not "
            "exist. Skipping."
        ] == caplog.messages
