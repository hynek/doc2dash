from __future__ import absolute_import, division, print_function

import os

from bs4 import BeautifulSoup
from zope.interface.verify import verifyObject

from doc2dash.parsers.intersphinx import (
    InterSphinxParser,
    find_and_patch_entry,
    _inv_to_entries,
)
from doc2dash.parsers.utils import IParser, ParserEntry, TOCEntry


HERE = os.path.dirname(__file__)


class TestInterSphinxParser(object):
    def test_interface(self):
        """
        InterSphinxParser fully implements IParser.
        """
        verifyObject(IParser, InterSphinxParser(doc_path="foo"))

    def test_parses(self):
        """
        Parsing of the example objects.inv in the current directory does not
        fail.
        """
        p = InterSphinxParser(doc_path=os.path.join(HERE))
        assert [] != list(p.parse())

    def test_inv_to_entries(self):
        """
        Inventory items are correctly converted.
        """
        result = list(
            _inv_to_entries({"py:method": {
                "some_method": (None, None, u"some_module.py", u"-"),
            }})
        )
        assert [ParserEntry(
            name='some_method', type='Method', path='some_module.py'
        )] == result


class TestFindAndPatchEntry(object):
    def test_patch_method(self):
        """
        Patching a method adds a TOC entry.
        """
        soup = BeautifulSoup(open(os.path.join(HERE, 'function_example.html')))
        assert True is find_and_patch_entry(
            soup,
            TOCEntry(
                name='pyramid.config.Configurator.add_route',
                type='Method',
                anchor='pyramid.config.Configurator.add_route',
            )
        )
        toc_link = soup(
            'a',
            attrs={
                'name': '//apple_ref/cpp/Method/pyramid.config.Configurator.'
                        'add_route'
            }
        )
        assert toc_link

    def test_patch_modules(self):
        """
        Patching a module adds the TOC entry into the next <h1>.
        """
        soup = BeautifulSoup(
            "<h1>Some Module</h1>",
        )
        assert True is find_and_patch_entry(
            soup,
            TOCEntry(
                name="some_module",
                type="Module",
                anchor="module-some_module",
            )
        )
        assert '<a name="//apple_ref' in str(soup)

    def test_patch_fail(self):
        """
        Return `False` if anchor can't be found
        """
        soup = BeautifulSoup(open(os.path.join(HERE, 'function_example.html')))
        assert False is find_and_patch_entry(
            soup,
            TOCEntry(
                name="foo",
                type="Nothing",
                anchor="does-not-exist",
            )
        )
