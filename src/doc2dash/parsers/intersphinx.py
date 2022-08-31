from __future__ import annotations

import logging

from pathlib import Path
from typing import ClassVar, Generator, Mapping

import attrs

from bs4 import BeautifulSoup

from . import entry_types
from .sphinx_inventory import InventoryEntry, load_inventory
from .types import ParserEntry
from .utils import format_ref, has_file_with


log = logging.getLogger(__name__)


# https://www.sphinx-doc.org/en/master/usage/restructuredtext/domains.html
# ->
# https://kapeli.com/docsets#supportedentrytypes
INV_TO_TYPE = {
    "attribute": entry_types.ATTRIBUTE,
    "class": entry_types.CLASS,
    "classmethod": entry_types.METHOD,
    "cmdoption": entry_types.OPTION,
    "constant": entry_types.CONSTANT,
    "data": entry_types.VALUE,
    "doc": entry_types.GUIDE,
    "envvar": entry_types.ENV,
    "exception": entry_types.EXCEPTION,
    "function": entry_types.FUNCTION,
    "interface": entry_types.INTERFACE,
    "label": entry_types.SECTION,
    "macro": entry_types.MACRO,
    "member": entry_types.ATTRIBUTE,
    "method": entry_types.METHOD,
    "module": entry_types.PACKAGE,
    "opcode": entry_types.OPCODE,
    "option": entry_types.OPTION,
    "property": entry_types.PROPERTY,
    "protocol": entry_types.PROTOCOL,
    "setting": entry_types.SETTING,
    "staticmethod": entry_types.METHOD,
    "term": entry_types.WORD,
    "type": entry_types.TYPE,
    "variable": entry_types.VARIABLE,
    "var": entry_types.VARIABLE,
}


@attrs.define
class InterSphinxParser:
    """
    Parser for Sphinx-base documentation that generates an objects.inv file for
    the intersphinx extension.
    """

    name: ClassVar[str] = "intersphinx"
    source: Path

    @staticmethod
    def detect(path: Path) -> bool:
        return has_file_with(
            path, "objects.inv", b"# Sphinx inventory version 2"
        )

    @staticmethod
    def guess_name(path: Path) -> str | None:
        with (path / "objects.inv").open("rb") as f:
            f.readline()  # Sphinx inventory...
            line = f.readline().decode().strip()

        assert line.startswith("# Project: ")

        return line[11:]

    def parse(self) -> Generator[ParserEntry, None, None]:
        """
        Parse sphinx docs at self.source

        yield `ParserEntry`s.
        """
        with (self.source / "objects.inv").open("rb") as inv_f:
            yield from self._inv_to_entries(load_inventory(inv_f))

    def find_and_patch_entry(
        self, soup: BeautifulSoup, name: str, type: str, anchor: str
    ) -> bool:
        return _find_and_patch_entry(soup, name, type, anchor)

    def _inv_to_entries(
        self, inv: Mapping[str, Mapping[str, InventoryEntry]]
    ) -> Generator[ParserEntry, None, None]:
        """
        Iterate over a dictionary as returned from Sphinx's object.inv parser
        and yield `ParserEntry`s.
        """
        for type_key, inv_entries in inv.items():
            dash_type = self.convert_type(type_key)
            if dash_type is None:
                continue

            for key, data in inv_entries.items():
                entry = self.create_entry(dash_type, key, data)
                if entry is not None:
                    yield entry

    def convert_type(self, inv_type: str) -> str | None:
        """
        Map an intersphinx type to a Dash type.

        Returns a Dash type string, or None to not construct entries.
        """
        try:
            return INV_TO_TYPE[inv_type.split(":")[-1]]
        except KeyError:  # pragma: no cover
            log.debug("convert_type: unknown type: %r", inv_type)

            return None

    def create_entry(
        self, dash_type: str, key: str, inv_entry: InventoryEntry
    ) -> ParserEntry:
        """
        Create a ParserEntry (or None) given inventory details

        Parameters are the dash type, intersphinx inventory key and data tuple.

        This is a method to allow customization by inheritance.
        """
        path_str = _clean_up_path(inv_entry[0])
        name = inv_entry[1] if inv_entry[1] != "-" else key

        return ParserEntry(name=name, type=dash_type, path=path_str)


def _find_and_patch_entry(
    soup: BeautifulSoup, name: str, type: str, anchor: str
) -> bool:
    """
    Modify *soup* so Dash.app can generate TOCs on the fly.
    """
    pos = None
    if type == entry_types.WORD:
        pos = soup.find("dt", id=anchor)
    elif type == entry_types.SECTION:
        pos = soup.find(id=anchor)
    elif anchor.startswith("module-"):
        pos = soup.h1

    if not pos:
        pos = (
            soup.find("a", {"class": "headerlink"}, href="#" + anchor)
            or soup.find(
                "a", {"class": "reference internal"}, href="#" + anchor
            )
            or soup.find("span", id=anchor)
        )

    if not pos:
        return False

    tag = soup.new_tag("a")
    tag["class"] = "dashAnchor"
    tag["name"] = format_ref(type, name)

    pos.insert_before(tag)

    return True


def _clean_up_path(path: str) -> str:
    """
    Clean up a path as it comes from an inventory.

    Discard the anchors between head and tail to make it
    compatible with situations where extra meta information is encoded.

    If the path ends with an "/", append an index.html.
    """
    path_tuple = path.split("#")
    if len(path_tuple) > 1:
        return f"{_maybe_index(path_tuple[0])}#{path_tuple[-1]}"

    return _maybe_index(path)


def _maybe_index(path: str) -> str:
    if path.endswith("/"):
        return f"{path}index.html"

    return path
