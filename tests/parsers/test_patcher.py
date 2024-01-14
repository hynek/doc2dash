# SPDX-FileCopyrightText: 2012 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import logging

from contextlib import contextmanager
from pathlib import Path
from typing import ClassVar

import attrs
import pytest

from doc2dash.parsers.patcher import patch_anchors
from doc2dash.parsers.types import EntryType, ParserEntry


@pytest.fixture(name="doc_entries")
def _doc_entries(tmp_path):
    """
    Test `ParserEntry`s
    """
    test_dir = tmp_path / "foo"
    test_dir.mkdir()
    (test_dir / "bar.html").write_text("docs!")
    (test_dir / "foo bar.html").write_text("docs too!")

    return test_dir, [
        ParserEntry(
            name="foo", type=EntryType.METHOD, path="bar.html#anchor-1"
        ),
        ParserEntry(name="qux", type=EntryType.CLASS, path="bar.html"),
        ParserEntry(
            name="foo-url",
            type=EntryType.METHOD,
            path="foo%20bar.html#anchor-2",
        ),
    ]


@attrs.define
class FakeParser:
    source: str
    _succeed_patching: bool = True
    _patched_entries: list = attrs.Factory(list)
    _patcher_closed: bool = False

    name: ClassVar[str] = "FakeParser"

    @staticmethod
    def detect(path):
        return True

    def parse(self):
        pass

    @contextmanager
    def make_patcher_for_file(self, path):
        if not path.exists():
            raise FileNotFoundError

        def patch(name, type, anchor, ref):
            if self._patched_entries is None:
                self._patched_entries = []

            self._patched_entries.append((name, type, anchor))

            return self._succeed_patching

        yield patch

        self._patcher_closed = True


class TestPatchTOCAnchors:
    @pytest.mark.parametrize("progressbar", [True, False])
    def test_with_empty_db(self, progressbar):
        """
        Adding no entries does not cause an error.
        """
        parser = FakeParser(source="foo")
        toc = patch_anchors(parser, Path("foo"), show_progressbar=progressbar)
        next(toc)
        toc.close()

    def test_single_entry(self, doc_entries):
        """
        Only entries with URL anchors get patched.
        """
        path, entries = doc_entries
        parser = FakeParser(source=path)

        toc = patch_anchors(parser, path, show_progressbar=False)
        next(toc)

        for e in entries:
            toc.send(e)
        toc.close()

        assert [
            ("foo", EntryType.METHOD, "anchor-1"),
            ("foo-url", EntryType.METHOD, "anchor-2"),
        ] == parser._patched_entries

    def test_missing_other_files_explode(self):
        """
        If a file is missing that is NOT py-modindex.html, an exception is
        raised.
        """
        parser = FakeParser(source="foo")
        toc = patch_anchors(parser, Path("foo"), show_progressbar=False)
        next(toc)

        toc.send(ParserEntry("Foo", EntryType.SECTION, "FooBarQux.html#"))

        with pytest.raises(FileNotFoundError):
            toc.close()

    def test_complains(self, doc_entries, caplog):
        """
        If patching fails, a debug message is logged.
        """
        from doc2dash.parsers.patcher import log

        old_level = log.getEffectiveLevel()
        log.setLevel(logging.DEBUG)

        path, entries = doc_entries

        parser = FakeParser(source=str(path), succeed_patching=False)
        toc = patch_anchors(parser, path, show_progressbar=False)
        next(toc)

        for e in entries:
            toc.send(e)

        toc.close()

        assert [
            "Can't find anchor 'anchor-1' (EntryType.METHOD) in 'bar.html'.",
            "Can't find anchor 'anchor-2' (EntryType.METHOD) in 'foo bar.html'"
            ".",  # lol
            "Failed to add anchors for 2 TOC entries.",
        ] == caplog.messages

        log.setLevel(old_level)
