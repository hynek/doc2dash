from __future__ import absolute_import, division, print_function

import codecs
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
                u"some_method": (None, None, u"some_module.py", u"-"),
            }, "std:option": {
                u"--destination": (
                    u"doc2dash",
                    u"2.0",
                    u"index.html#document-usage#cmdoption--destination",
                    u"-"
                )
            }, "std:constant": {
                u"SomeConstant": (None, None, u"some_other_module.py", u"-")
            }})
        )
        assert set([ParserEntry(
            name=u'some_method', type=u'Method', path=u'some_module.py'
            ),
            ParserEntry(
                name=u'--destination',
                type=u'Option',
                path=u'index.html#cmdoption--destination'
            ),
            ParserEntry(
                name=u'SomeConstant',
                type=u'Constant',
                path=u'some_other_module.py',
            )
        ]) == set(result)


class TestFindAndPatchEntry(object):
    def test_patch_method(self):
        """
        Patching a method adds a TOC entry.
        """
        soup = BeautifulSoup(
            codecs.open(os.path.join(HERE, 'function_example.html'),
                        mode="r", encoding="utf-8")
        )
        assert True is find_and_patch_entry(
            soup,
            TOCEntry(
                name=u'pyramid.config.Configurator.add_route',
                type=u'Method',
                anchor=u'pyramid.config.Configurator.add_route',
            )
        )
        toc_link = soup(
            u'a',
            attrs={
                u'name': u'//apple_ref/cpp/Method/pyramid.config.Configurator.'
                         u'add_route'
            }
        )
        assert toc_link

    def test_patch_modules(self):
        """
        Patching a module adds the TOC entry into the next <h1>.  Non-ASCII
        works.
        """
        soup = BeautifulSoup(
            u"<h1>Some Module</h1>",
        )
        assert True is find_and_patch_entry(
            soup,
            TOCEntry(
                name=u"some_module",
                type=u"M\xc3\xb6dule",
                anchor=u"module-some_module",
            )
        )
        assert '<a name="//apple_ref' in str(soup)

    def test_patch_fail(self):
        """
        Return `False` if anchor can't be found
        """
        soup = BeautifulSoup(
            codecs.open(os.path.join(HERE, 'function_example.html'),
                        mode="r", encoding="utf-8")
        )
        assert False is find_and_patch_entry(
            soup,
            TOCEntry(
                name=u"foo",
                type=u"Nothing",
                anchor=u"does-not-exist",
            )
        )
