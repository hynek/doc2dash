import errno
import os

from bs4 import BeautifulSoup
from mock import patch
from pytest import raises

from doc2dash.parsers import sphinx, types
from doc2dash.parsers.base import Entry


HERE = os.path.dirname(__file__)


def test_index_detection(tmpdir):
    """
    TODO: This is a terrible way to big test that need to get refactored.
    """
    parser = sphinx.SphinxParser(str(tmpdir))
    with raises(IOError) as e:
        list(parser.parse())
    assert e.value.errno == errno.ENOENT

    idx_all = tmpdir.join('genindex-all.html')
    idx = tmpdir.join('genindex.html')
    idx_all.write('all')
    idx.write('reg')

    with patch('doc2dash.parsers.sphinx._parse_soup') as mock:
        list(parser.parse())
        assert 'all' in str(mock.call_args[0][0])
        idx_all.remove()
        list(parser.parse())
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
    soup = BeautifulSoup(open(os.path.join(HERE, 'dd_example.html')))
    assert (list(sphinx._process_dd('__call__()', soup)) ==
            DD_EXAMPLE_PARSE_RESULT)
    assert list(sphinx._process_dd(
        'foo()',
        BeautifulSoup('<dd><dl><dt>doesntmatchanything</dt></dl><dd>'))) == []


def test_guess_type_by_name():
    assert sphinx._guess_type_by_name('foo()') == types.FUNCTION
    assert sphinx._guess_type_by_name('foo') == types.CONSTANT


EXAMPLE_PARSE_RESULT = [
    ('pyramid.interfaces.IResponse.__call__', types.METHOD,
     'api/interfaces.html#pyramid.interfaces.IResponse.__call__'),
    ('pyramid.interfaces.IRoutePregenerator.__call__', types.METHOD,
     'api/interfaces.html#pyramid.interfaces.IRoutePregenerator.__call__'),
    ('pyramid.interfaces.ISessionFactory.__call__', types.METHOD,
     'api/interfaces.html#pyramid.interfaces.ISessionFactory.__call__'),
    ('pyramid.interfaces.IViewMapper.__call__', types.METHOD,
     'api/interfaces.html#pyramid.interfaces.IViewMapper.__call__'),
    ('pyramid.interfaces.IViewMapperFactory.__call__', types.METHOD,
     'api/interfaces.html#pyramid.interfaces.IViewMapperFactory.__call__'),
    ('pyramid.interfaces.IDict.__contains__', types.METHOD,
     'api/interfaces.html#pyramid.interfaces.IDict.__contains__'),
    ('pyramid.interfaces.IDict.__delitem__', types.METHOD,
     'api/interfaces.html#pyramid.interfaces.IDict.__delitem__'),
    ('pyramid.interfaces.IDict.__getitem__', types.METHOD,
     'api/interfaces.html#pyramid.interfaces.IDict.__getitem__'),
    ('pyramid.interfaces.IIntrospectable.__hash__', types.METHOD,
     'api/interfaces.html#pyramid.interfaces.IIntrospectable.__hash__'),
    ('pyramid.interfaces.IDict.__iter__', types.METHOD,
     'api/interfaces.html#pyramid.interfaces.IDict.__iter__'),
    ('pyramid.interfaces.IDict.__setitem__', types.METHOD,
     'api/interfaces.html#pyramid.interfaces.IDict.__setitem__'),
    ('pyramid.interfaces.IActionInfo.__str__', types.METHOD,
     'api/interfaces.html#pyramid.interfaces.IActionInfo.__str__'),
    ('dict', types.CLASS, 'library/stdtypes.html#dict'),
    ('ftplib.FTP.abort', types.METHOD,
     'library/ftplib.html#ftplib.FTP.abort'),
    ('os.abort', types.FUNCTION, 'library/os.html#os.abort'),
    ('qux', types.CONSTANT, 'api/foo#qux'),
    ('abc', types.PACKAGE, 'library/abc.html#module-abc'),
    ('BINARY_AND', types.CONSTANT, 'library/dis.html#opcode-BINARY_AND'),
]


def test_parse_soup(monkeypatch):
    monkeypatch.setattr(sphinx, 'POSSIBLE_INDEXES', ['sphinx_example.html'])
    res = list(sphinx.SphinxParser(HERE).parse())
    soup = BeautifulSoup(open(os.path.join(HERE, 'sphinx_example.html')))
    assert res == list(sphinx._parse_soup(soup))
    assert res == EXAMPLE_PARSE_RESULT


def test_strip_annotation():
    assert sphinx._strip_annotation('Foo') == 'Foo'
    assert sphinx._strip_annotation('foo()') == 'foo()'
    assert sphinx._strip_annotation('Foo (bar)') == 'Foo'
    assert sphinx._strip_annotation('foo() (bar baz)') == 'foo()'
    assert sphinx._strip_annotation('foo() ()') == 'foo()'


def test_patcher():
    p = sphinx.SphinxParser('foo')
    soup = BeautifulSoup(open(os.path.join(HERE, 'function_example.html')))
    assert p.find_and_patch_entry(
        soup,
        Entry(
            'pyramid.config.Configurator.add_route',
            'clm',
            'pyramid.config.Configurator.add_route'
        )
    )
    toc_link = soup(
        'a',
        attrs={'name': '//apple_ref/cpp/clm/pyramid.config.Configurator.'
                       'add_route'}
    )
    assert toc_link
    assert not p.find_and_patch_entry(soup, Entry('invented', 'cl', 'nonex'))
    assert p.find_and_patch_entry(soup, Entry('somemodule', 'cl', 'module-sm'))
