import logging

from pathlib import Path
from typing import ClassVar

import attrs
import pytest

from doc2dash.parsers.patcher import patch_anchors
from doc2dash.parsers.types import IParser, ParserEntry, TOCEntry
from doc2dash.parsers.utils import has_file_with


@attrs.define
class FakeParser(IParser):
    doc_path: str
    _succeed_patching: bool = True
    _patched_entries: list = attrs.Factory(list)

    name: ClassVar[str] = "FakeParser"

    @staticmethod
    def detect(path):
        return True

    def parse(self):
        pass

    def find_and_patch_entry(self, soup, entry):
        if self._patched_entries is None:
            self._patched_entries = []
        self._patched_entries.append(entry)
        return self._succeed_patching


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
        ParserEntry(name="foo", type="Method", path="bar.html#anchor-1"),
        ParserEntry(name="qux", type="Class", path="bar.html"),
        ParserEntry(
            name="foo-url", type="Method", path="foo%20bar.html#anchor-2"
        ),
    ]


class TestPatchTOCAnchors:
    @pytest.mark.parametrize("progressbar", [True, False])
    def test_with_empty_db(self, progressbar):
        """
        Adding no entries does not cause an error.
        """
        parser = FakeParser(doc_path="foo")
        toc = patch_anchors(parser, show_progressbar=progressbar)
        toc.close()

    def test_single_entry(self, doc_entries):
        """
        Only entries with URL anchors get patched.
        """
        path, entries = doc_entries
        parser = FakeParser(doc_path=str(path))

        toc = patch_anchors(parser, show_progressbar=False)
        for e in entries:
            toc.send(e)
        toc.close()

        assert [
            TOCEntry(name="foo", type="Method", anchor="anchor-1"),
            TOCEntry(name="foo-url", type="Method", anchor="anchor-2"),
        ] == parser._patched_entries

    def test_missing_py_modindex_html(self, caplog):
        """
        If py-modindex.html is missing, warn about it but keep going.

        Cf. https://github.com/hynek/doc2dash/issues/115
        """
        parser = FakeParser(doc_path="foo")
        toc = patch_anchors(parser, show_progressbar=False)

        toc.send(ParserEntry("Module Index", "label", "py-modindex.html#"))

        toc.close()

        assert [
            "Can't open file foo/py-modindex.html. Skipping."
        ] == caplog.messages

    def test_missing_other_files_explode(self):
        """
        If a file is missing that is NOT py-modindex.html, an exception is
        raised.
        """
        parser = FakeParser(doc_path="foo")
        toc = patch_anchors(parser, show_progressbar=False)

        toc.send(ParserEntry("Foo", "label", "FooBarQux.html#"))

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

        parser = FakeParser(doc_path=str(path), succeed_patching=False)
        toc = patch_anchors(parser, show_progressbar=False)
        for e in entries:
            toc.send(e)

        toc.close()

        assert [
            "Can't find anchor 'anchor-1' (Method) in 'bar.html'.",
            "Can't find anchor 'anchor-2' (Method) in 'foo bar.html'.",
        ] == caplog.messages

        log.setLevel(old_level)


class TestHasFileWith:
    @pytest.mark.parametrize(
        "content,has", [(b"xxxfooxxx", True), (b"xxxbarxxx", False)]
    )
    def test_exists(self, tmp_path, content, has):
        """
        If file contains content, return True, else False.
        """
        f = tmp_path / "test.txt"
        f.write_bytes(content)

        assert has is has_file_with(tmp_path, "test.txt", b"foo")

    def test_eent(self):
        """
        If file doesn't exist, return False.
        """
        assert False is has_file_with(Path("foo"), "bar", b"")

    def test_error(self, tmp_path):
        """
        If opening/reading fails with a different error, propagate.
        """
        f = tmp_path / "test.txt"
        f.write_bytes(b"foo")
        f.chmod(0)

        with pytest.raises(PermissionError):
            has_file_with(tmp_path, "test.txt", b"foo")
