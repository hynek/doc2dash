import codecs
import os

from unittest.mock import mock_open, patch

from bs4 import BeautifulSoup

from doc2dash.parsers import types
from doc2dash.parsers.pydoctor import PyDoctorParser
from doc2dash.parsers.utils import ParserEntry, TOCEntry


HERE = os.path.dirname(__file__)

EXAMPLE_PARSE_RESULT = [
    ParserEntry(name=t[0], type=t[1], path=t[2])
    for t in [
        (
            "twisted.conch.insults.insults.ServerProtocol"
            ".ControlSequenceParser.A",
            types.METHOD,
            "twisted.conch.insults.insults.ServerProtocol"
            ".ControlSequenceParser.html#A",
        ),
        (
            "twisted.test.myrebuilder1.A",
            types.CLASS,
            "twisted.test.myrebuilder1.A.html",
        ),
        (
            "twisted.test.myrebuilder2.A",
            types.CLASS,
            "twisted.test.myrebuilder2.A.html",
        ),
        (
            "twisted.test.test_jelly.A",
            types.CLASS,
            "twisted.test.test_jelly.A.html",
        ),
        (
            "twisted.test.test_persisted.A",
            types.CLASS,
            "twisted.test.test_persisted.A.html",
        ),
        (
            "twisted.internet.task.LoopingCall.a",
            types.VARIABLE,
            "twisted.internet.task.LoopingCall.html#a",
        ),
        (
            "twisted.test.myrebuilder1.A.a",
            types.METHOD,
            "twisted.test.myrebuilder1.A.html#a",
        ),
        (
            "twisted.test.myrebuilder1.Inherit.a",
            types.METHOD,
            "twisted.test.myrebuilder1.Inherit.html#a",
        ),
        (
            "twisted.test.myrebuilder2.A.a",
            types.METHOD,
            "twisted.test.myrebuilder2.A.html#a",
        ),
        (
            "twisted.test.myrebuilder2.Inherit.a",
            types.METHOD,
            "twisted.test.myrebuilder2.Inherit.html#a",
        ),
        (
            "twisted.web._newclient.HTTP11ClientProtocol.abort",
            types.METHOD,
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
        print(list(PyDoctorParser(doc_path="foo").parse()))
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
