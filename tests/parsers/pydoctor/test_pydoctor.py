import codecs
import os

from unittest.mock import mock_open, patch

from bs4 import BeautifulSoup

from doc2dash.parsers import entry_types
from doc2dash.parsers.pydoctor import PyDoctorParser
from doc2dash.parsers.types import ParserEntry, TOCEntry


HERE = os.path.dirname(__file__)

EXAMPLE_PARSE_RESULT = [
    ParserEntry(name=t[0], type=t[1], path=t[2])
    for t in [
        (
            "twisted.conch.insults.insults.ServerProtocol"
            ".ControlSequenceParser.A",
            entry_types.METHOD,
            "twisted.conch.insults.insults.ServerProtocol"
            ".ControlSequenceParser.html#A",
        ),
        (
            "twisted.test.myrebuilder1.A",
            entry_types.CLASS,
            "twisted.test.myrebuilder1.A.html",
        ),
        (
            "twisted.test.myrebuilder2.A",
            entry_types.CLASS,
            "twisted.test.myrebuilder2.A.html",
        ),
        (
            "twisted.test.test_jelly.A",
            entry_types.CLASS,
            "twisted.test.test_jelly.A.html",
        ),
        (
            "twisted.test.test_persisted.A",
            entry_types.CLASS,
            "twisted.test.test_persisted.A.html",
        ),
        (
            "twisted.internet.task.LoopingCall.a",
            entry_types.VARIABLE,
            "twisted.internet.task.LoopingCall.html#a",
        ),
        (
            "twisted.test.myrebuilder1.A.a",
            entry_types.METHOD,
            "twisted.test.myrebuilder1.A.html#a",
        ),
        (
            "twisted.test.myrebuilder1.Inherit.a",
            entry_types.METHOD,
            "twisted.test.myrebuilder1.Inherit.html#a",
        ),
        (
            "twisted.test.myrebuilder2.A.a",
            entry_types.METHOD,
            "twisted.test.myrebuilder2.A.html#a",
        ),
        (
            "twisted.test.myrebuilder2.Inherit.a",
            entry_types.METHOD,
            "twisted.test.myrebuilder2.Inherit.html#a",
        ),
        (
            "twisted.web._newclient.HTTP11ClientProtocol.abort",
            entry_types.METHOD,
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
            list(PyDoctorParser(doc_path="foo").parse())
            == EXAMPLE_PARSE_RESULT
        )


def test_patcher():
    p = PyDoctorParser(doc_path="foo")
    with codecs.open(
        os.path.join(HERE, "function_example.html"), mode="r", encoding="utf-8"
    ) as fp:
        soup = BeautifulSoup(fp, "html.parser")

    assert p.find_and_patch_entry(
        soup,
        TOCEntry(
            name="twisted.application.app.ApplicationRunner.startReactor",
            type="clm",
            anchor="startReactor",
        ),
    )
    toc_link = soup(
        "a",
        attrs={
            "name": "//apple_ref/cpp/clm/twisted.application.app."
            "ApplicationRunner.startReactor"
        },
    )
    assert toc_link
    next_tag = toc_link[0].next_sibling
    assert next_tag.name == "a"
    assert next_tag["name"] == "startReactor"
    assert not p.find_and_patch_entry(
        soup, TOCEntry(name="invented", type="cl", anchor="nonex")
    )
