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


DD_EXAMPLE_PARSE_RESULT = [
        ('pyramid.interfaces.IRoutePregenerator.__call__', types.METHOD,
         'api/interfaces.html#pyramid.interfaces.IRoutePregenerator.__call__'),
        ('pyramid.interfaces.ISessionFactory.__call__', types.METHOD,
         'api/interfaces.html#pyramid.interfaces.ISessionFactory.__call__'),
        ('pyramid.interfaces.IViewMapper.__call__', types.FUNCTION,
         'api/interfaces.html#pyramid.interfaces.IViewMapper.__call__'),
        ('pyramid.interfaces.IViewMapperFactory.__call__', types.METHOD,
         'api/interfaces.html#pyramid.interfaces.IViewMapperFactory.__call__'),
]


def test_process_dd():
    soup = BeautifulSoup(open('tests/parsers/sphinx/dd_example.html'))
    assert list(parser._process_dd('__call__()', soup)) == \
           DD_EXAMPLE_PARSE_RESULT
    assert list(parser._process_dd(
        'foo',
        BeautifulSoup('<dd><dl><dt>doesntmatchanything</dt></dl><dd>'))) == []


def test_guess_type_by_name():
    assert parser._guess_type_by_name('foo()') == types.FUNCTION
    assert parser._guess_type_by_name('foo') == types.CONSTANT


EXAMPLE_PARSE_RESULT = [
        ('pyramid.interfaces.IResponse.__call__', 'clm',
         'api/interfaces.html#pyramid.interfaces.IResponse.__call__'),
        ('pyramid.interfaces.IRoutePregenerator.__call__', 'clm',
         'api/interfaces.html#pyramid.interfaces.IRoutePregenerator.__call__'),
        ('pyramid.interfaces.ISessionFactory.__call__', 'clm',
         'api/interfaces.html#pyramid.interfaces.ISessionFactory.__call__'),
        ('pyramid.interfaces.IViewMapper.__call__', 'clm',
         'api/interfaces.html#pyramid.interfaces.IViewMapper.__call__'),
        ('pyramid.interfaces.IViewMapperFactory.__call__', 'clm',
         'api/interfaces.html#pyramid.interfaces.IViewMapperFactory.__call__'),
        ('pyramid.interfaces.IDict.__contains__', 'clm',
         'api/interfaces.html#pyramid.interfaces.IDict.__contains__'),
        ('pyramid.interfaces.IDict.__delitem__', 'clm',
         'api/interfaces.html#pyramid.interfaces.IDict.__delitem__'),
        ('pyramid.interfaces.IDict.__getitem__', 'clm',
         'api/interfaces.html#pyramid.interfaces.IDict.__getitem__'),
        ('pyramid.interfaces.IIntrospectable.__hash__', 'clm',
         'api/interfaces.html#pyramid.interfaces.IIntrospectable.__hash__'),
        ('pyramid.interfaces.IDict.__iter__', 'clm',
         'api/interfaces.html#pyramid.interfaces.IDict.__iter__'),
        ('pyramid.interfaces.IDict.__setitem__', 'clm',
         'api/interfaces.html#pyramid.interfaces.IDict.__setitem__'),
        ('pyramid.interfaces.IActionInfo.__str__', 'clm',
         'api/interfaces.html#pyramid.interfaces.IActionInfo.__str__'),
        ('dict', 'cl', 'library/stdtypes.html#dict'),
        ('qux', 'clconst', 'api/foo#qux'),
]


def test_parse_soup(monkeypatch):
    monkeypatch.setattr(parser, 'POSSIBLE_INDEXES', ['sphinx_example.html'])
    res = list(parser.parse('tests/parsers/sphinx'))
    soup = BeautifulSoup(open('tests/parsers/sphinx/sphinx_example.html'))
    assert res == list(parser._parse_soup(soup))
    assert res == EXAMPLE_PARSE_RESULT


def test_strip_annotation():
    assert parser._strip_annotation('Foo') == 'Foo'
    assert parser._strip_annotation('foo()') == 'foo'
    assert parser._strip_annotation('Foo (bar)') == 'Foo'
    assert parser._strip_annotation('foo() (bar baz)') == 'foo'
    assert parser._strip_annotation('foo() ()') == 'foo'
