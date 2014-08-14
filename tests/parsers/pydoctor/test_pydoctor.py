from __future__ import absolute_import, division, print_function

import os

import pytest

from bs4 import BeautifulSoup
from mock import patch, mock_open
from zope.interface.verify import verifyObject

from doc2dash.parsers import types
from doc2dash.parsers.pydoctor import PyDoctorParser, _guess_type
from doc2dash.parsers.utils import IParser, TOCEntry, ParserEntry


HERE = os.path.dirname(__file__)


class TestPyDoctorParser(object):
    def test_interface(self):
        """
        PyDoctorParser fully implements IParser.
        """
        verifyObject(IParser, PyDoctorParser(doc_path="foo"))


@pytest.mark.parametrize(
    "name, path, expected", [
        ('startServer',
         'twisted.conch.test.test_cftp.CFTPClientTestBase.html#startServer',
         types.METHOD
         ),
        ('A', 'twisted.test.myrebuilder1.A.html', types.CLASS),
        ('epollreactor', 'twisted.internet.epollreactor.html',
         types.PACKAGE)
    ]
)
def test_guess_type(name, path, expected):
    """
    Symbol types are correctly guessed.
    """
    assert _guess_type(name, path) == expected


EXAMPLE_PARSE_RESULT = [
    ParserEntry(name=t[0], type=t[1], path=t[2])
    for t in [
        ('twisted.conch.insults.insults.ServerProtocol'
         '.ControlSequenceParser.A', types.METHOD,
         'twisted.conch.insults.insults.ServerProtocol'
         '.ControlSequenceParser.html#A'),
        ('twisted.test.myrebuilder1.A', types.CLASS,
         'twisted.test.myrebuilder1.A.html'),
        ('twisted.test.myrebuilder2.A', types.CLASS,
         'twisted.test.myrebuilder2.A.html'),
        ('twisted.test.test_jelly.A', types.CLASS,
         'twisted.test.test_jelly.A.html'),
        ('twisted.test.test_persisted.A', types.CLASS,
         'twisted.test.test_persisted.A.html'),
        ('twisted.test.myrebuilder1.A.a', types.METHOD,
         'twisted.test.myrebuilder1.A.html#a'),
        ('twisted.test.myrebuilder1.Inherit.a', types.METHOD,
         'twisted.test.myrebuilder1.Inherit.html#a'),
        ('twisted.test.myrebuilder2.A.a', types.METHOD,
         'twisted.test.myrebuilder2.A.html#a'),
        ('twisted.test.myrebuilder2.Inherit.a', types.METHOD,
         'twisted.test.myrebuilder2.Inherit.html#a'),
        ('twisted.web._newclient.HTTP11ClientProtocol.abort', types.METHOD,
         'twisted.web._newclient.HTTP11ClientProtocol.html#abort')
    ]]


def test_parse():
    """
    The shipped example results in the expected parsing result.
    """
    example = open(os.path.join(HERE, 'pydoctor_example.html')).read()
    with patch('doc2dash.parsers.pydoctor.open', mock_open(read_data=example),
               create=True):
        assert (list(PyDoctorParser(doc_path='foo').parse())
                == EXAMPLE_PARSE_RESULT)


def test_patcher():
    p = PyDoctorParser(doc_path='foo')
    soup = BeautifulSoup(open(os.path.join(HERE, 'function_example.html')))
    assert p.find_and_patch_entry(
        soup,
        TOCEntry(name='twisted.application.app.ApplicationRunner.startReactor',
                 type='clm', anchor='startReactor')
    )
    toc_link = soup(
        'a',
        attrs={'name': '//apple_ref/cpp/clm/twisted.application.app.'
                       'ApplicationRunner.startReactor'}
    )
    assert toc_link
    next_tag = toc_link[0].next_sibling
    assert next_tag.name == 'a'
    assert (next_tag['name'] == 'startReactor')
    assert not p.find_and_patch_entry(
        soup, TOCEntry(name='invented', type='cl', anchor='nonex')
    )
