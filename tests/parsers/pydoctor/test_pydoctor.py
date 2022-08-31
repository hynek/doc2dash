import codecs
import os

from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from bs4 import BeautifulSoup

from doc2dash.parsers.pydoctor import PyDoctorParser, _has_file_with
from doc2dash.parsers.types import EntryType, ParserEntry


HERE = os.path.dirname(__file__)

EXAMPLE_PARSE_RESULT = [
    ParserEntry(name=t[0], type=t[1], path=t[2])
    for t in [
        (
            "twisted.conch.insults.insults.ServerProtocol"
            ".ControlSequenceParser.A",
            EntryType.METHOD,
            "twisted.conch.insults.insults.ServerProtocol"
            ".ControlSequenceParser.html#A",
        ),
        (
            "twisted.test.myrebuilder1.A",
            EntryType.CLASS,
            "twisted.test.myrebuilder1.A.html",
        ),
        (
            "twisted.test.myrebuilder2.A",
            EntryType.CLASS,
            "twisted.test.myrebuilder2.A.html",
        ),
        (
            "twisted.test.test_jelly.A",
            EntryType.CLASS,
            "twisted.test.test_jelly.A.html",
        ),
        (
            "twisted.test.test_persisted.A",
            EntryType.CLASS,
            "twisted.test.test_persisted.A.html",
        ),
        (
            "twisted.internet.task.LoopingCall.a",
            EntryType.VARIABLE,
            "twisted.internet.task.LoopingCall.html#a",
        ),
        (
            "twisted.test.myrebuilder1.A.a",
            EntryType.METHOD,
            "twisted.test.myrebuilder1.A.html#a",
        ),
        (
            "twisted.test.myrebuilder1.Inherit.a",
            EntryType.METHOD,
            "twisted.test.myrebuilder1.Inherit.html#a",
        ),
        (
            "twisted.test.myrebuilder2.A.a",
            EntryType.METHOD,
            "twisted.test.myrebuilder2.A.html#a",
        ),
        (
            "twisted.test.myrebuilder2.Inherit.a",
            EntryType.METHOD,
            "twisted.test.myrebuilder2.Inherit.html#a",
        ),
        (
            "twisted.web._newclient.HTTP11ClientProtocol.abort",
            EntryType.METHOD,
            "twisted.web._newclient.HTTP11ClientProtocol.html#abort",
        ),
    ]
]


def test_parse():
    """
    The shipped example results in the expected parsing result.
    """
    with codecs.open(
        os.path.join(HERE, "pydoctor_example.html"), mode="r", encoding="utf-8"
    ) as fp:
        example = fp.read()

    with patch(
        "doc2dash.parsers.pydoctor.codecs.open",
        mock_open(read_data=example),
        create=True,
    ):
        assert (
            list(PyDoctorParser(source="foo").parse()) == EXAMPLE_PARSE_RESULT
        )


def test_patcher():
    p = PyDoctorParser(source="foo")
    with codecs.open(
        os.path.join(HERE, "function_example.html"), mode="r", encoding="utf-8"
    ) as fp:
        soup = BeautifulSoup(fp, "html.parser")

    assert p.find_and_patch_entry(
        soup,
        name="twisted.application.app.ApplicationRunner.startReactor",
        type=EntryType.METHOD,
        anchor="startReactor",
    )

    toc_link = soup(
        "a",
        attrs={
            "name": "//apple_ref/cpp/Method/twisted.application.app."
            "ApplicationRunner.startReactor"
        },
    )

    assert toc_link

    next_tag = toc_link[0].next_sibling

    assert next_tag.name == "a"
    assert next_tag["name"] == "startReactor"
    assert not p.find_and_patch_entry(
        soup, name="invented", type=EntryType.CLASS, anchor="nonex"
    )


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

        assert has is _has_file_with(tmp_path, "test.txt", b"foo")

    def test_eent(self):
        """
        If file doesn't exist, return False.
        """
        assert False is _has_file_with(Path("foo"), "bar", b"")

    def test_error(self, tmp_path):
        """
        If opening/reading fails with a different error, propagate.
        """
        f = tmp_path / "test.txt"
        f.write_bytes(b"foo")
        f.chmod(0)

        with pytest.raises(PermissionError):
            _has_file_with(tmp_path, "test.txt", b"foo")
