from __future__ import absolute_import, division, print_function

import errno
import os

import pytest

from bs4 import BeautifulSoup
from mock import patch
from zope.interface.verify import verifyObject

from doc2dash.parsers import sphinx, types
from doc2dash.parsers.utils import IParser, ParserEntry


HERE = os.path.dirname(__file__)


class TestSphinxParser(object):
    def test_interface(self):
        """
        SphinxParser fully implements IParser.
        """
        verifyObject(IParser, sphinx.SphinxParser(doc_path="foo"))

    def test_missing_index(self, tmpdir):
        """
        Raises IOError with ENOENT if neither genindex.html nor
        genindex-all.html are present.
        """
        parser = sphinx.SphinxParser(doc_path=str(tmpdir))
        with pytest.raises(IOError) as e:
            list(parser.parse())
        assert e.value.errno == errno.ENOENT

    @pytest.mark.parametrize(
        "index",
        ["genindex.html", "genindex-all.html"]
    )
    def test_finds_index(self, tmpdir, index):
        """
        Finds either genindex.html or genindex-all.html.
        """
        parser = sphinx.SphinxParser(doc_path=str(tmpdir))
        idx = tmpdir.join(index)
        idx.write("content")
        with patch('doc2dash.parsers.sphinx._parse_soup') as mock:
            list(parser.parse())
            assert 'content' in str(mock.call_args[0][0])


DD_EXAMPLE_PARSE_RESULT = [
    ParserEntry(name=t[0], type=t[1], path=t[2]) for t in [
        ('pyramid.interfaces.IRoutePregenerator.__call__', types.METHOD,
         'api/interfaces.html#pyramid.interfaces.IRoutePregenerator.__call__'),
        ('pyramid.interfaces.ISessionFactory.__call__', types.METHOD,
         'api/interfaces.html#pyramid.interfaces.ISessionFactory.__call__'),
        ('pyramid.interfaces.IViewMapper.__call__', types.FUNCTION,
         'api/interfaces.html#pyramid.interfaces.IViewMapper.__call__'),
        ('pyramid.interfaces.IViewMapperFactory.__call__', types.METHOD,
         'api/interfaces.html#pyramid.interfaces.IViewMapperFactory.__call__'),
    ]
]


class TestProcessDD(object):
    def test_success(self):
        soup = BeautifulSoup(open(os.path.join(HERE, 'dd_example.html')))
        assert (list(sphinx._process_dd('__call__()', soup)) ==
                DD_EXAMPLE_PARSE_RESULT)

    def test_failure(self):
        assert list(sphinx._process_dd(
            'foo()',
            BeautifulSoup('<dd><dl><dt>doesntmatchanything</dt></dl><dd>'))
        ) == []


@pytest.mark.parametrize(
    "name, expected_type", [
        ("foo()", types.FUNCTION),
        ("foo", types.CONSTANT),
    ]
)
def test_guess_type_by_name(name, expected_type):
    """
    Types are guessed correctly according to the name of a symbol.
    """
    assert expected_type == sphinx._guess_type_by_name(name)


EXAMPLE_PARSE_RESULT = [
    ParserEntry(name=t[0], type=t[1], path=t[2]) for t in [
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
]


def test_parse_soup(monkeypatch):
    monkeypatch.setattr(sphinx, 'POSSIBLE_INDEXES', ['sphinx_example.html'])
    res = list(sphinx.SphinxParser(doc_path=HERE).parse())
    soup = BeautifulSoup(open(os.path.join(HERE, 'sphinx_example.html')))
    assert res == list(sphinx._parse_soup(soup))
    assert res == EXAMPLE_PARSE_RESULT


@pytest.mark.parametrize(
    "name, clean", [
        ("Foo", "Foo"),
        ("foo()", "foo()"),
        ("Foo (bar)", "Foo"),
        ("foo() (bar baz)", "foo()"),
        ("foo() ()", "foo()"),
    ]
)
def test_strip_annotation(name, clean):
    """
    Annotations are stripped but names and parantheses of functions/methods
    aren't mangled.
    """
    assert clean == sphinx._strip_annotation(name)
