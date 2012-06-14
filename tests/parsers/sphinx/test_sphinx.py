import errno
import os
import tempfile

from bs4 import BeautifulSoup
from mock import patch
from pytest import raises

from doc2dash.parsers.sphinx import parser
from doc2dash.parsers import types


def test_index_detection():
    with tempfile.TemporaryDirectory() as td:
        with raises(IOError) as e:
            list(parser.parse(td))
        assert e.value.errno == errno.ENOENT

        idx_all = os.path.join(td, 'genindex-all.html')
        idx = os.path.join(td, 'genindex.html')
        with open(idx_all, 'w') as f1, \
             open(idx, 'w') as f2:
            f1.write('all')
            f2.write('reg')

        with patch('doc2dash.parsers.sphinx.parser._parse_soup') as mock:
            list(parser.parse(td))
            assert 'all' in str(mock.call_args[0][0])
            os.unlink(idx_all)
            list(parser.parse(td))
            assert 'reg' in str(mock.call_args[0][0])


def test_process_dd():
    soup = BeautifulSoup(open('tests/parsers/sphinx/dd_example.html'))
    assert list(parser._process_dd('__call__()', soup)) == [
            ('__call__()', types.METHOD, 'api/interfaces.html#'
                'pyramid.interfaces.IRoutePregenerator.__call__'),
            ('__call__()', types.METHOD, 'api/interfaces.html#'
                'pyramid.interfaces.ISessionFactory.__call__'),
            ('__call__()', types.FUNCTION, 'api/interfaces.html#'
                'pyramid.interfaces.IViewMapper.__call__'),
            ('__call__()', types.METHOD, 'api/interfaces.html#'
                'pyramid.interfaces.IViewMapperFactory.__call__'),
    ]

    assert list(parser._process_dd(
        'foo',
        BeautifulSoup('<dd><dl><dt>doesntmatchanything</dt></dl><dd>'))) == []


def test_guess_type_by_name():
    assert parser._guess_type_by_name('foo()') == types.FUNCTION
    assert parser._guess_type_by_name('foo') == types.CONSTANT


def test_parse_soup(monkeypatch):
    monkeypatch.setattr(parser, 'POSSIBLE_INDEXES', ['sphinx_example.html'])
    res = list(parser.parse('tests/parsers/sphinx'))
    soup = BeautifulSoup(open('tests/parsers/sphinx/sphinx_example.html'))
    assert res == list(parser._parse_soup(soup))
    assert res == [
            ('__call__()', 'clm', 'api/interfaces.html#'
                'pyramid.interfaces.IResponse.__call__'),
            ('__call__()', 'clm', 'api/interfaces.html#'
                'pyramid.interfaces.IRoutePregenerator.__call__'),
            ('__call__()', 'clm', 'api/interfaces.html#'
                'pyramid.interfaces.ISessionFactory.__call__'),
            ('__call__()', 'clm', 'api/interfaces.html#'
                'pyramid.interfaces.IViewMapper.__call__'),
            ('__call__()', 'clm', 'api/interfaces.html#'
                'pyramid.interfaces.IViewMapperFactory.__call__'),
            ('__contains__()', 'clm', 'api/interfaces.html#'
                'pyramid.interfaces.IDict.__contains__'),
            ('__delitem__()', 'clm', 'api/interfaces.html#'
                'pyramid.interfaces.IDict.__delitem__'),
            ('__getitem__()', 'clm', 'api/interfaces.html#'
                'pyramid.interfaces.IDict.__getitem__'),
            ('__hash__()', 'clm', 'api/interfaces.html#'
                'pyramid.interfaces.IIntrospectable.__hash__'),
            ('__iter__()', 'clm', 'api/interfaces.html#'
                'pyramid.interfaces.IDict.__iter__'),
            ('__setitem__()', 'clm', 'api/interfaces.html#'
                'pyramid.interfaces.IDict.__setitem__'),
            ('__str__()', 'clm', 'api/interfaces.html#'
                'pyramid.interfaces.IActionInfo.__str__'),
            ('foo', 'clconst', 'api/foo'),
    ]
