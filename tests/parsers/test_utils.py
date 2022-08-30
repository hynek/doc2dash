from __future__ import annotations

from pathlib import Path

import pytest

from doc2dash.parsers.utils import has_file_with


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
