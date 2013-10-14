import os

from bs4 import BeautifulSoup
from mock import patch, mock_open

from doc2dash.parsers import types
from doc2dash.parsers.base import Entry
from doc2dash.parsers.pydoctor import PyDoctorParser, _guess_type


HERE = os.path.dirname(__file__)


def test_guess_type():
    ts = [
        ('startServer',
         'twisted.conch.test.test_cftp.CFTPClientTestBase.html#startServer',
         types.METHOD),
        ('A', 'twisted.test.myrebuilder1.A.html', types.CLASS),
        ('epollreactor', 'twisted.internet.epollreactor.html',
         types.PACKAGE)
    ]

    for t in ts:
        assert _guess_type(t[0], t[1]) == t[2]


EXAMPLE_PARSE_RESULT = [
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
]


def test_parse():
    example = open(os.path.join(HERE, 'pydoctor_example.html')).read()
    with patch('doc2dash.parsers.pydoctor.open', mock_open(read_data=example),
               create=True):
        assert list(PyDoctorParser('foo').parse()) == EXAMPLE_PARSE_RESULT


def test_patcher():
    p = PyDoctorParser('foo')
    soup = BeautifulSoup(open(os.path.join(HERE, 'function_example.html')))
    assert p.find_and_patch_entry(
        soup,
        Entry('twisted.application.app.ApplicationRunner.startReactor',
              'clm', 'startReactor')
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
    assert not p.find_and_patch_entry(soup, Entry('invented', 'cl', 'nonex'))
