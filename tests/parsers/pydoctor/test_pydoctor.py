from __future__ import absolute_import, division, print_function

import codecs
import os

from bs4 import BeautifulSoup
from mock import patch, mock_open
from zope.interface.verify import verifyObject

from doc2dash.parsers import types
from doc2dash.parsers.pydoctor import PyDoctorParser
from doc2dash.parsers.utils import IParser, TOCEntry, ParserEntry


HERE = os.path.dirname(__file__)


class TestPyDoctorParser(object):
    def test_interface(self):
        """
        PyDoctorParser fully implements IParser.
        """
        verifyObject(IParser, PyDoctorParser(doc_path=u"foo"))


EXAMPLE_PARSE_RESULT = [
    ParserEntry(name=t[0], type=t[1], path=t[2])
    for t in [
        (u'twisted.conch.insults.insults.ServerProtocol'
         u'.ControlSequenceParser.A', types.METHOD,
         u'twisted.conch.insults.insults.ServerProtocol'
         u'.ControlSequenceParser.html#A'),
        (u'twisted.test.myrebuilder1.A', types.CLASS,
         u'twisted.test.myrebuilder1.A.html'),
        (u'twisted.test.myrebuilder2.A', types.CLASS,
         u'twisted.test.myrebuilder2.A.html'),
        (u'twisted.test.test_jelly.A', types.CLASS,
         u'twisted.test.test_jelly.A.html'),
        (u'twisted.test.test_persisted.A', types.CLASS,
         u'twisted.test.test_persisted.A.html'),
        (u'twisted.internet.task.LoopingCall.a', types.VARIABLE,
         u'twisted.internet.task.LoopingCall.html#a'),
        (u'twisted.test.myrebuilder1.A.a', types.METHOD,
         u'twisted.test.myrebuilder1.A.html#a'),
        (u'twisted.test.myrebuilder1.Inherit.a', types.METHOD,
         u'twisted.test.myrebuilder1.Inherit.html#a'),
        (u'twisted.test.myrebuilder2.A.a', types.METHOD,
         u'twisted.test.myrebuilder2.A.html#a'),
        (u'twisted.test.myrebuilder2.Inherit.a', types.METHOD,
         u'twisted.test.myrebuilder2.Inherit.html#a'),
        (u'twisted.web._newclient.HTTP11ClientProtocol.abort', types.METHOD,
         u'twisted.web._newclient.HTTP11ClientProtocol.html#abort')
    ]]


def test_parse():
    """
    The shipped example results in the expected parsing result.
    """
    example = codecs.open(
        os.path.join(HERE, 'pydoctor_example.html'),
        mode="r", encoding="utf-8",
    ).read()
    with patch('doc2dash.parsers.pydoctor.codecs.open',
               mock_open(read_data=example),
               create=True):
        print(list(PyDoctorParser(doc_path=u'foo').parse()))
        assert list(
            PyDoctorParser(doc_path=u'foo').parse()
        ) == EXAMPLE_PARSE_RESULT


def test_patcher():
    p = PyDoctorParser(doc_path=u'foo')
    soup = BeautifulSoup(
        codecs.open(
            os.path.join(HERE, 'function_example.html'),
            mode="r", encoding="utf-8"
        ),
        "lxml",
    )
    assert p.find_and_patch_entry(
        soup,
        TOCEntry(
            name=u'twisted.application.app.ApplicationRunner.startReactor',
            type=u'clm', anchor=u'startReactor'
        )
    )
    toc_link = soup(
        'a',
        attrs={'name': u'//apple_ref/cpp/clm/twisted.application.app.'
               u'ApplicationRunner.startReactor'}
    )
    assert toc_link
    next_tag = toc_link[0].next_sibling
    assert next_tag.name == u'a'
    assert (next_tag['name'] == u'startReactor')
    assert not p.find_and_patch_entry(
        soup, TOCEntry(name=u'invented', type=u'cl', anchor=u'nonex')
    )
