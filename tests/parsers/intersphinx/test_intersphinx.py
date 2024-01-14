# SPDX-FileCopyrightText: 2012 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

from pathlib import Path

import pytest

from bs4 import BeautifulSoup

from doc2dash.parsers.intersphinx import (
    InterSphinxParser,
    _find_entry_and_add_ref,
)
from doc2dash.parsers.types import EntryType, ParserEntry


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
                            "index.html#cmdoption--destination",
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
                type=EntryType.METHOD,
                path="some_module.py",
            ),
            ParserEntry(
                name="--destination",
                type=EntryType.OPTION,
                path="index.html#cmdoption--destination",
            ),
            ParserEntry(
                name="SomeConstant",
                type=EntryType.CONSTANT,
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
                    return None
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
                type=EntryType.CONSTANT,
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
                path_str = inv_entry[0]
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
                name="!some_method!",
                type=EntryType.METHOD,
                path="some_module.py",
            )
        ] == result

    def test_create_entry_none(self, sphinx_built):
        """
        `create_entry` can return None.
        """

        class MyInterSphinxParser(InterSphinxParser):
            def create_entry(self, dash_type, key, inv_entry):
                if dash_type == EntryType.OPTION:
                    return None
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
                name="some_method",
                type=EntryType.METHOD,
                path="some_module.py",
            )
        ] == result


@pytest.fixture(name="soup")
def _soup():
    return BeautifulSoup(
        (Path(HERE) / "function_example.html").read_text(encoding="utf-8"),
        "html.parser",
    )


@pytest.fixture(name="pydoctor_soup")
def _pydoctor_soup():
    return BeautifulSoup(
        (Path(HERE) / "pydoctor_example.html").read_text(encoding="utf-8"),
        "html.parser",
    )


class TestFindAndPatchEntry:
    def test_patch_method(self, soup):
        """
        Patching a method adds a TOC entry.
        """
        assert True is _find_entry_and_add_ref(
            soup,
            name="pyramid.config.Configurator.add_route",
            type=EntryType.METHOD,
            anchor="pyramid.config.Configurator.add_route",
            ref="//apple_ref/cpp/Method/pyramid.config.Configurator.add_route",
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
        Patching a module adds the TOC entry into the next <h1>.
        """
        soup = BeautifulSoup("<h1>Some Module</h1>", "html.parser")

        assert True is _find_entry_and_add_ref(
            soup,
            name="some_module",
            type=EntryType.PACKAGE,
            anchor="module-some_module",
            ref="//apple_ref/cpp/Module/pyramid.security",
        )
        assert '<a class="dashAnchor" name="//apple_ref' in str(soup)

    def test_patch_fail(self, soup):
        """
        Return `False` if anchor can't be found
        """
        assert False is _find_entry_and_add_ref(
            soup,
            name="foo",
            type="Nothing",
            anchor="does-not-exist",
            ref="does-not-matter",
        )

    def test_patch_term(self, soup):
        """
        :term: and glossaries are found.
        """
        ref = "//apple_ref/cpp/Word/Whatever"

        assert True is _find_entry_and_add_ref(
            soup,
            name="Whatever",
            type=EntryType.WORD,
            anchor="term-dict-classes",
            ref=ref,
        )
        assert (
            f'<a class="dashAnchor" name="{ref}"></a>'
            '<dt id="term-dict-classes">' in str(soup)
        )

    def test_patch_section(self, soup):
        """
        Sections are found.
        """
        ref = "//apple_ref/cpp/Section/Chains"

        assert True is _find_entry_and_add_ref(
            soup,
            name="Chains",
            type=EntryType.SECTION,
            anchor="chains",
            ref=ref,
        )
        assert (
            f'<a class="dashAnchor" name="{ref}"></a>'
            '<section id="chains">' in str(soup)
        )

    def test_pydoctor_class(self, pydoctor_soup):
        """
        Pydoctor classes are found.
        """
        ref = "//apple_ref/cpp/Word/twisted._threads._convenience.Quit.isSet"

        patched = _find_entry_and_add_ref(
            pydoctor_soup,
            name="twisted._threads._convenience.Quit.isSet",
            type=EntryType.WORD,
            anchor="isSet",
            ref=ref,
        )

        assert patched
        assert (
            f'<a class="dashAnchor" name="{ref}"></a>'
            '<a name="twisted._threads._convenience.Quit.isSet">'
            in str(pydoctor_soup)
        )


class TestIntersphinxDetect:
    def test_does_not_exist(self, tmp_path):
        """
        Empty paths without an objects.inv return None.
        """
        assert None is InterSphinxParser.detect(tmp_path)

    @pytest.mark.parametrize(
        "obj",
        [
            "",
            "# Sphinx inventory version 2",
            "# Sphinx inventory version 2\n",
            "# Sphinx inventory version 2\nFoo",
            "# Sphinx inventory version 2\nProject",
            "# Sphinx inventory version 2\nProject:",
            "# Sphinx inventory version 2\nProject: ",
        ],
    )
    def test_corrupt(self, tmp_path, caplog, obj):
        """
        Empty paths without an objects.inv return None.
        """
        (tmp_path / "objects.inv").write_text(obj)

        assert None is InterSphinxParser.detect(tmp_path)
        assert (
            f"intersphinx: object.inv at {tmp_path} exists, but is corrupt."
            == caplog.records[0].message
        )
