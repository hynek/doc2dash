from unittest.mock import patch

import attr
import pytest

from doc2dash.parsers.utils import (
    IParser,
    ParserEntry,
    TOCEntry,
    has_file_with,
    patch_anchors,
)


@attr.s
class FakeParser(IParser):
    doc_path = attr.ib(validator=attr.validators.instance_of(str))
    _succeed_patching = attr.ib(default=True)
    _patched_entries = attr.ib(default=attr.Factory(list))

    name = "FakeParser"

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


@pytest.fixture
def entries():
    """
    Test `ParserEntry`s
    """
    return [
        ParserEntry(name="foo", type="Method", path="bar.html#foo"),
        ParserEntry(name="qux", type="Class", path="bar.html"),
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

    def test_single_entry(self, monkeypatch, tmpdir, entries):
        """
        Only entries with URL anchors get patched.
        """
        foo = tmpdir.mkdir("foo")
        foo.join("bar.html").write("docs!")
        parser = FakeParser(doc_path=str(foo))
        toc = patch_anchors(parser, show_progressbar=False)
        for e in entries:
            print(e)
            toc.send(e)
        toc.close()
        assert [
            TOCEntry(name="foo", type="Method", anchor="foo")
        ] == parser._patched_entries

    def test_complains(self, entries, tmpdir):
        """
        If patching fails, a debug message is logged.
        """
        foo = tmpdir.mkdir("foo")
        foo.join("bar.html").write("docs!")
        parser = FakeParser(doc_path=str(foo), succeed_patching=False)
        toc = patch_anchors(parser, show_progressbar=False)
        for e in entries:
            toc.send(e)
        with patch("doc2dash.parsers.utils.log.debug") as mock:
            toc.close()
            assert mock.call_count == 1


class TestHasFileWith:
    @pytest.mark.parametrize(
        "content,has", [(b"xxxfooxxx", True), (b"xxxbarxxx", False)]
    )
    def test_exists(self, tmpdir, content, has):
        """
        If file contains content, return True, ealse False.
        """
        f = tmpdir.join("test")
        f.write(content)

        assert has is has_file_with("/", str(f), b"foo")

    def test_eent(self):
        """
        If file doesn't exist, return False.
        """
        assert False is has_file_with("foo", "bar", b"")

    def test_error(self, tmpdir):
        """
        If opening/reading fails with a differnt error, propate.
        """
        f = tmpdir.join("test")
        f.write(b"foo")
        f.chmod(0)

        with pytest.raises(PermissionError):
            has_file_with("/", str(f), "foo")
