from pathlib import Path

import pytest

from bs4 import BeautifulSoup

from doc2dash.parsers import entry_types
from doc2dash.parsers.intersphinx import (
    InterSphinxParser,
    _clean_up_path,
    _find_and_patch_entry,
)
from doc2dash.parsers.types import ParserEntry


HERE = Path(__file__).parent


class TestInterSphinxParser:
    def test_parses(self, sphinx_built):
        """
        Parsing of the example objects.inv in the current directory does not
        fail.
        """
        p = InterSphinxParser(source=sphinx_built)

        assert [] != list(p.parse())

    def test_inv_to_entries(self, sphinx_built):
        """
        Inventory items are correctly converted.
        """
        p = InterSphinxParser(source=sphinx_built)
        result = list(
            p._inv_to_entries(
                {
                    "py:method": {"some_method": ("some_module.py", "-")},
                    "std:option": {
                        "--destination": (
                            "index.html#document-usage#cmdoption--"
                            "destination",
                            "-",
                        )
                    },
                    "std:constant": {
                        "SomeConstant": (
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

    def test_convert_type_override(self, sphinx_built):
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

        p = MyInterSphinxParser(source=sphinx_built)
        result = list(
            p._inv_to_entries(
                {
                    "py:method": {"some_method": ("some_module.py", "-")},
                    "std:constant": {
                        "SomeConstant": (
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

    def test_create_entry_override(self, sphinx_built):
        """
        `create_entry` has the expected interface and can be overridden.

        We check that the name format can be adjusted.
        """

        class MyInterSphinxParser(InterSphinxParser):
            def create_entry(self, dash_type, key, inv_entry):
                path_str = _clean_up_path(inv_entry[0])
                return ParserEntry(
                    name=f"!{key}!", type=dash_type, path=path_str
                )

        p = MyInterSphinxParser(source=sphinx_built)
        result = list(
            p._inv_to_entries(
                {"py:method": {"some_method": ("some_module.py", "-")}}
            )
        )
        assert [
            ParserEntry(
                name="!some_method!", type="Method", path="some_module.py"
            )
        ] == result

    def test_create_entry_none(self, sphinx_built):
        """
        `create_entry` can return None.
        """

        class MyInterSphinxParser(InterSphinxParser):
            def create_entry(self, dash_type, key, inv_entry):
                if dash_type == "Option":
                    return
                return super().create_entry(dash_type, key, inv_entry)

        p = MyInterSphinxParser(source=sphinx_built)
        result = list(
            p._inv_to_entries(
                {
                    "py:method": {"some_method": ("some_module.py", "-")},
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
        (Path(HERE) / "function_example.html").read_text(),
        "html.parser",
    )


class TestFindAndPatchEntry:
    def test_patch_method(self, soup):
        """
        Patching a method adds a TOC entry.
        """
        assert True is _find_and_patch_entry(
            soup,
            name="pyramid.config.Configurator.add_route",
            type="Method",
            anchor="pyramid.config.Configurator.add_route",
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
        assert True is _find_and_patch_entry(
            soup,
            name="some_module",
            type="M\xc3\xb6dule",
            anchor="module-some_module",
        )
        assert '<a class="dashAnchor" name="//apple_ref' in str(soup)

    def test_patch_fail(self, soup):
        """
        Return `False` if anchor can't be found
        """
        assert False is _find_and_patch_entry(
            soup, name="foo", type="Nothing", anchor="does-not-exist"
        )

    def test_patch_term(self, soup):
        """
        :term: and glossaries are found.
        """
        assert True is _find_and_patch_entry(
            soup,
            name="Whatever",
            type=entry_types.WORD,
            anchor="term-dict-classes",
        )
        assert (
            '<a class="dashAnchor" name="//apple_ref/cpp/Word/Whatever"></a>'
            '<dt id="term-dict-classes">' in str(soup)
        )

    def test_patch_section(self, soup):
        """
        Sections are found.
        """
        assert True is _find_and_patch_entry(
            soup, name="Chains", type=entry_types.SECTION, anchor="chains"
        )
        assert (
            '<a class="dashAnchor" name="//apple_ref/cpp/Section/Chains"></a>'
            '<section id="chains">' in str(soup)
        )


@pytest.mark.parametrize(
    "path,expected",
    [
        ("docs.html", "docs.html"),
        ("docs/", "docs/index.html"),
        ("docs.html#api", "docs.html#api"),
        ("docs/#api", "docs/index.html#api"),
        ("docs.html#foo#api", "docs.html#api"),
        ("docs/#foo#api", "docs/index.html#api"),
    ],
)
def test_cleanup_path(path, expected):
    """
    Paths without an anchor are passed through.
    """
    assert expected == _clean_up_path(path)
