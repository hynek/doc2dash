import os
import pathlib

import pytest

from bs4 import BeautifulSoup

from doc2dash.parsers import types
from doc2dash.parsers.intersphinx import (
    InterSphinxParser,
    find_and_patch_entry,
    inv_entry_to_path,
)
from doc2dash.parsers.utils import ParserEntry, TOCEntry


HERE = os.path.dirname(__file__)


class TestInterSphinxParser:
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
        p = InterSphinxParser(doc_path=os.path.join(HERE))
        result = list(
            p._inv_to_entries(
                {
                    "py:method": {
                        "some_method": (None, None, "some_module.py", "-")
                    },
                    "std:option": {
                        "--destination": (
                            "doc2dash",
                            "2.0",
                            "index.html#document-usage#cmdoption--"
                            "destination",
                            "-",
                        )
                    },
                    "std:constant": {
                        "SomeConstant": (
                            None,
                            None,
                            "some_other_module.py",
                            "-",
                        )
                    },
                }
            )
        )
        assert {
            ParserEntry(
                name="some_method",
                type="Method",
                path="some_module.py",
            ),
            ParserEntry(
                name="--destination",
                type="Option",
                path="index.html#cmdoption--destination",
            ),
            ParserEntry(
                name="SomeConstant",
                type="Constant",
                path="some_other_module.py",
            ),
        } == set(result)

    def test_convert_type_override(self):
        """
        `convert_type` can be overridden.

        We check that we can hide some key of choice.
        """

        class MyInterSphinxParser(InterSphinxParser):
            def convert_type(self, inv_type):
                if inv_type == "py:method":
                    # hide method entries
                    return
                return super().convert_type(inv_type)

        p = MyInterSphinxParser(doc_path=os.path.join(HERE))
        result = list(
            p._inv_to_entries(
                {
                    "py:method": {
                        "some_method": (None, None, "some_module.py", "-")
                    },
                    "std:constant": {
                        "SomeConstant": (
                            None,
                            None,
                            "some_other_module.py",
                            "-",
                        )
                    },
                }
            )
        )
        assert [
            ParserEntry(
                name="SomeConstant",
                type="Constant",
                path="some_other_module.py",
            )
        ] == result

    def test_create_entry_override(self):
        """
        `create_entry` has the expected interface and can be overridden.

        We check that the name format can be adjusted.
        """

        class MyInterSphinxParser(InterSphinxParser):
            def create_entry(self, dash_type, key, inv_entry):
                path_str = inv_entry_to_path(inv_entry)
                return ParserEntry(
                    name=f"!{key}!", type=dash_type, path=path_str
                )

        p = MyInterSphinxParser(doc_path=os.path.join(HERE))
        result = list(
            p._inv_to_entries(
                {
                    "py:method": {
                        "some_method": (None, None, "some_module.py", "-")
                    }
                }
            )
        )
        assert [
            ParserEntry(
                name="!some_method!", type="Method", path="some_module.py"
            )
        ] == result

    def test_create_entry_none(self):
        """
        `create_entry` can return None.
        """

        class MyInterSphinxParser(InterSphinxParser):
            def create_entry(self, dash_type, key, inv_entry):
                if dash_type == "Option":
                    return
                return super().create_entry(dash_type, key, inv_entry)

        p = MyInterSphinxParser(doc_path=os.path.join(HERE))
        result = list(
            p._inv_to_entries(
                {
                    "py:method": {
                        "some_method": (None, None, "some_module.py", "-")
                    },
                    "std:option": {
                        "--destination": (
                            "doc2dash",
                            "2.0",
                            "index.html#document-usage#cmdoption--"
                            "destination",
                            "-",
                        )
                    },
                }
            )
        )
        assert [
            ParserEntry(
                name="some_method", type="Method", path="some_module.py"
            )
        ] == result


@pytest.fixture(name="soup")
def _soup():
    return BeautifulSoup(
        (pathlib.Path(HERE) / "function_example.html").read_text(),
        "html.parser",
    )


class TestFindAndPatchEntry:
    def test_patch_method(self, soup):
        """
        Patching a method adds a TOC entry.
        """
        assert True is find_and_patch_entry(
            soup,
            TOCEntry(
                name="pyramid.config.Configurator.add_route",
                type="Method",
                anchor="pyramid.config.Configurator.add_route",
            ),
        )

        toc_link = soup(
            "a",
            attrs={
                "name": "//apple_ref/cpp/Method/pyramid.config.Configurator."
                "add_route"
            },
        )

        assert toc_link

    def test_patch_modules(self):
        """
        Patching a module adds the TOC entry into the next <h1>.  Non-ASCII
        works.
        """
        soup = BeautifulSoup("<h1>Some Module</h1>", "html.parser")
        assert True is find_and_patch_entry(
            soup,
            TOCEntry(
                name="some_module",
                type="M\xc3\xb6dule",
                anchor="module-some_module",
            ),
        )
        assert '<a class="dashAnchor" name="//apple_ref' in str(soup)

    def test_patch_fail(self, soup):
        """
        Return `False` if anchor can't be found
        """
        assert False is find_and_patch_entry(
            soup, TOCEntry(name="foo", type="Nothing", anchor="does-not-exist")
        )

    def test_patch_term(self, soup):
        """
        :term: and glossaries are found.
        """
        assert True is find_and_patch_entry(
            soup,
            TOCEntry(
                name="Whatever", type=types.WORD, anchor="term-dict-classes"
            ),
        )
        assert (
            '<a class="dashAnchor" name="//apple_ref/cpp/Word/Whatever"></a>'
            '<dt id="term-dict-classes">' in str(soup)
        )

    def test_patch_section(self, soup):
        """
        Sections are found.
        """
        assert True is find_and_patch_entry(
            soup,
            TOCEntry(name="Chains", type=types.SECTION, anchor="chains"),
        )
        assert (
            '<a class="dashAnchor" name="//apple_ref/cpp/Section/Chains"></a>'
            '<section id="chains">' in str(soup)
        )
