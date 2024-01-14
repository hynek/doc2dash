# SPDX-FileCopyrightText: 2012 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import errno
import logging
import os
import sqlite3
import subprocess
import sys

from pathlib import Path
from typing import ClassVar
from unittest.mock import Mock

import attrs
import pytest

from click.testing import CliRunner

import doc2dash

from doc2dash import __main__ as main
from doc2dash import docsets
from doc2dash.parsers.types import EntryType, ParserEntry


log = logging.getLogger(__name__)


@pytest.fixture(name="runner")
def _runner():
    """
    Click's test helper.
    """
    return CliRunner()


def test_intersphinx(runner: CliRunner, tmp_path: Path, sphinx_built: Path):
    """
    Convert our test project and look at the result.

    Use verbose mode to catch warnings about missing TOCs anchors.
    """
    result = runner.invoke(
        main.main,
        [str(sphinx_built), "-v", "-d", str(tmp_path)],
        catch_exceptions=False,
    )

    assert "Can't find anchor" not in result.output

    docset = tmp_path / "sphinx-example.docset"
    contents = docset / "Contents"
    resources = contents / "Resources"

    assert 0 == result.exit_code
    assert {
        "CFBundleIdentifier": "sphinx-example",
        "CFBundleName": "sphinx-example",
        "DashDocSetDeclaredInStyle": "originalName",
        "DashDocSetFamily": "python",
        "DocSetPlatformFamily": "sphinx-example",
        "isDashDocset": True,
        "isJavaScriptEnabled": False,
    } == docsets.read_plist(contents / "Info.plist")

    conn = sqlite3.connect(resources / "docSet.dsidx")
    curs = conn.execute("SELECT name, type, path FROM searchIndex")
    rows = set(curs.fetchall())
    curs.close()
    conn.close()

    assert {
        ("--foo", "Option", "index.html#cmdoption-foo"),
        ("ENV_VARIABLE", "Environment", "index.html#envvar-ENV_VARIABLE"),
        ("Foobar", "Word", "glossary.html#term-Foobar"),
        ("A Glossary", "Guide", "glossary.html"),
        ("mwt", "Word", "glossary.html#term-mwt"),
        ("multi-word term", "Word", "glossary.html#term-multi-word-term"),
        ("Index", "Section", "genindex.html"),
        (
            "Let’s define some symbols and see if doc2dash can handle them!",
            "Guide",
            "index.html",
        ),
        ("Module Index", "Section", "py-modindex.html"),
        ("Python Module Index", "Section", "py-modindex.html"),
        ("Search Page", "Section", "search.html"),
        ("some_module", "Module", "index.html#module-some_module"),
        (
            "some_module.BoringData",
            "Value",
            "index.html#some_module.BoringData",
        ),
        ("some_module.LeClass", "Class", "index.html#some_module.LeClass"),
        (
            "some_module.LeClass.AnAttr",
            "Attribute",
            "index.html#some_module.LeClass.AnAttr",
        ),
        (
            "some_module.LeClass.DieMethod",
            "Method",
            "index.html#some_module.LeClass.DieMethod",
        ),
        (
            "some_module.LeClass.Mine",
            "Property",
            "index.html#some_module.LeClass.Mine",
        ),
        ("some_module.func", "Function", "index.html#some_module.func"),
    } == rows


class TestArguments:
    def test_fails_with_unknown_icon(self, runner, tmp_path):
        """
        Fail if icon is not PNG.
        """
        p = tmp_path / "sub" / "bar.png"
        p.parent.mkdir()
        p.write_text("GIF89afoobarbaz")

        result = runner.invoke(main.main, [str(tmp_path), "-i", str(p)])

        assert result.output.endswith(" is not a valid PNG image.\n")
        assert errno.EINVAL == result.exit_code

    def test_fails_with_missing_index_page(
        self, runner, sphinx_built, tmp_path
    ):
        """
        Fail if --index-page file is missing.
        """
        result = runner.invoke(
            main.main,
            [str(sphinx_built), "-d", str(tmp_path), "--index-page", "xxx"],
        )

        assert (
            f'Index page "xxx" does not exist within "{sphinx_built}".\n'
            == result.output
        )

    def test_handles_unknown_doc_types(self, runner, tmp_path):
        """
        If existing docs are passed but are unknown, exit with EINVAL.
        """
        (tmp_path / "readme.txt").write_text("unknown docs")

        result = runner.invoke(main.main, [str(tmp_path)])

        assert errno.EINVAL == result.exit_code

    def test_quiet_and_verbose_conflict(self, runner, tmp_path):
        """
        Ensure main() exits on -q + -v
        """
        result = runner.invoke(main.main, [str(tmp_path), "-q", "-v"])

        assert 1 == result.exit_code
        assert "makes no sense" in result.output

    def test_fails_if_supplied_parser_fails(self, runner, tmp_path):
        """
        If a parser is passed using --parser/-P and doesn't recognize the docs,
        exit with EINVAL.
        """
        result = runner.invoke(
            main.main,
            [
                "--parser",
                "doc2dash.parsers.intersphinx.InterSphinxParser",
                str(tmp_path),
            ],
        )

        assert errno.EINVAL == result.exit_code
        assert (
            "Supplied parser <class "
            "'doc2dash.parsers.intersphinx.InterSphinxParser'> can't parse "
            f"'{tmp_path}'.\n" == result.output
        )


def test_normal_flow(monkeypatch, tmp_path, runner):
    """
    Integration test with a mock parser.
    """

    def fake_prepare(
        source,
        dest,
        name,
        index_page,
        enable_js,
        online_redirect_url,
        playground_url,
        icon,
        icon_2x,
        full_text_search,
    ):
        os.mkdir(dest)
        db_conn = sqlite3.connect(":memory:")
        db_conn.row_factory = sqlite3.Row
        db_conn.execute(
            "CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, "
            "type TEXT, path TEXT)"
        )

        return docsets.DocSet(path=tmp_path, plist=None, db_conn=db_conn)

    monkeypatch.chdir(tmp_path)
    png_file = tmp_path / "icon.png"
    png_file.write_bytes(main.PNG_HEADER)

    src = Path("foo").absolute()
    src.mkdir()
    monkeypatch.setattr(docsets, "prepare_docset", fake_prepare)

    @attrs.define
    class FakeParser:
        name: ClassVar[str] = "testtype"
        source: str

        @staticmethod
        def detect(path):
            return "bahh"

        def parse(self):
            yield ParserEntry(
                name="testmethod", type=EntryType.METHOD, path="testpath"
            )

        def make_patcher_for_file(self, path):
            pass

    class fake_module:  # noqa: N801
        Parser = FakeParser

    expected = f"""\
Converting testtype docs from '{src}' to '{{name}}.docset'.
Parsing documentation...
Added 1 index entries.
"""

    # alternative 1: use --parser
    sys.modules["fake_module"] = fake_module
    run_mock = Mock(spec_set=subprocess.check_output)
    monkeypatch.setattr(subprocess, "check_output", run_mock)

    result = runner.invoke(
        main.main,
        [
            "foo",
            "--parser",
            "fake_module.Parser",
            "-n",
            "bah",
            "-a",
            "-i",
            str(png_file),
        ],
        catch_exceptions=False,
    )

    assert (
        expected.format(name="bah")
        == result.output.split("Patching for TOCs...")[0]
    ), result.output.split("Patching for TOCs...")[0]
    assert 0 == result.exit_code
    assert (("open", "-a", "dash", Path("bah.docset")),) == run_mock.call_args[
        0
    ]

    # alternative 2: patch doc2dash.parsers
    monkeypatch.setattr(
        doc2dash.parsers, "get_doctype", lambda _: (FakeParser, "baz")
    )
    run_mock.reset_mock()

    result = runner.invoke(
        main.main,
        ["foo", "-n", "bar", "-a", "-i", str(png_file)],
        catch_exceptions=False,
    )

    assert (
        expected.format(name="bar")
        == result.output.split("Patching for TOCs...")[0]
    )
    assert 0 == result.exit_code
    assert (("open", "-a", "dash", Path("bar.docset")),) == run_mock.call_args[
        0
    ]

    # Again, just without adding and icon.
    run_mock.reset_mock()
    result = runner.invoke(
        main.main,
        ["foo", "-n", "baz"],
        catch_exceptions=False,
    )

    assert 0 == result.exit_code

    # some tests for --parser validation

    result = runner.invoke(
        main.main,
        ["foo", "-n", "bing", "--parser", "no_dot"],
        catch_exceptions=False,
    )

    assert (
        "'no_dot' is not an import path"
        in result.output.split("Patching files for TOCs...")[0]
    )
    assert 2 == result.exit_code

    result = runner.invoke(
        main.main,
        ["foo", "-n", "bing", "--parser", "nonexistent_module.Parser"],
        catch_exceptions=False,
    )

    assert "Could not import module 'nonexistent_module'" in result.output
    assert 2 == result.exit_code

    result = runner.invoke(
        main.main,
        ["foo", "-n", "bing", "--parser", "sys.NonexistentParser"],
        catch_exceptions=False,
    )

    assert (
        "Failed to get attribute 'NonexistentParser' from module 'sys'"
        in result.output
    )
    assert 2 == result.exit_code


class TestSetupPaths:
    def test_works(self, tmp_path):
        """
        Integration tests with fake paths.
        """
        foo_path = tmp_path / "foo"
        docset = tmp_path / "foo.docset"
        foo_path.mkdir()

        assert docset == main.setup_destination(
            tmp_path,
            name="foo",
            add_to_global=False,
            force=False,
        )

        assert (tmp_path / "baz.docset") == main.setup_destination(
            tmp_path,
            name="baz",
            add_to_global=False,
            force=False,
        )

    def test_add_to_global_overrides_destination(self):
        """
        Passing -A computes the destination and overrides an argument.
        """
        assert main.DEFAULT_DOCSET_PATH.is_absolute
        assert (
            main.DEFAULT_DOCSET_PATH / "foo.docset"
        ) == main.setup_destination(
            destination=Path("foobar"),
            name="foo",
            add_to_global=True,
            force=False,
        )

    def test_detects_existing_dest(self, tmp_path, monkeypatch):
        """
        Exit with EEXIST if the selected destination already exists.
        """
        monkeypatch.chdir(tmp_path)
        (tmp_path / "foo.docset").mkdir()

        with pytest.raises(SystemExit) as e:
            main.setup_destination(
                destination=Path("."),
                name="foo",
                force=False,
                add_to_global=False,
            )
        assert e.value.code == errno.EEXIST

        main.setup_destination(
            destination=Path("."),
            name="foo",
            force=True,
            add_to_global=False,
        )
        assert not os.path.lexists("foo.docset")
