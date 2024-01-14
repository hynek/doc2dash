# SPDX-FileCopyrightText: 2012 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import logging

from contextlib import contextmanager
from pathlib import Path
from typing import ClassVar, Generator, Iterator, Mapping

import attrs

from bs4 import BeautifulSoup

from .intersphinx_inventory import InventoryEntry, load_inventory
from .types import EntryType, ParserEntry, Patcher


log = logging.getLogger(__name__)


# https://www.sphinx-doc.org/en/master/usage/restructuredtext/domains.html
# ->
# https://kapeli.com/docsets#supportedentrytypes
INV_TO_TYPE = {
    "attribute": EntryType.ATTRIBUTE,
    "attr": EntryType.ATTRIBUTE,  # mkdocstrings
    "class": EntryType.CLASS,
    "classmethod": EntryType.METHOD,
    "cmdoption": EntryType.OPTION,
    "constant": EntryType.CONSTANT,
    "data": EntryType.VALUE,
    "doc": EntryType.GUIDE,
    "envvar": EntryType.ENV,
    "exception": EntryType.EXCEPTION,
    "function": EntryType.FUNCTION,
    "interface": EntryType.INTERFACE,
    "label": EntryType.SECTION,
    "macro": EntryType.MACRO,
    "member": EntryType.ATTRIBUTE,
    "method": EntryType.METHOD,
    "module": EntryType.PACKAGE,
    "opcode": EntryType.OPCODE,
    "option": EntryType.OPTION,
    "property": EntryType.PROPERTY,
    "protocol": EntryType.PROTOCOL,
    "setting": EntryType.SETTING,
    "staticmethod": EntryType.METHOD,
    "term": EntryType.WORD,
    "type": EntryType.TYPE,
    "variable": EntryType.VARIABLE,
    "var": EntryType.VARIABLE,
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
    def detect(path: Path) -> str | None:
        try:
            with (path / "objects.inv").open("rb") as f:
                if f.readline() != b"# Sphinx inventory version 2\n":
                    log.warning(
                        "intersphinx: object.inv at %s exists, "
                        "but is corrupt.",
                        path,
                    )
                    return None

                t = f.readline().split(b": ", 1)
                if len(t) != 2 or t[0] != b"# Project":
                    log.warning(
                        "intersphinx: object.inv at %s exists, "
                        "but is corrupt.",
                        path,
                    )
                    return None

                return t[1].strip().decode()
        except FileNotFoundError:
            return None

    def parse(self) -> Generator[ParserEntry, None, None]:
        """
        Parse sphinx docs at self.source

        yield `ParserEntry`s.
        """
        yield from self._inv_to_entries(load_inventory(self.source))

    @contextmanager
    def make_patcher_for_file(self, path: Path) -> Iterator[Patcher]:
        with path.open(encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")

        def patch(name: str, type: EntryType, anchor: str, ref: str) -> bool:
            return _find_entry_and_add_ref(soup, name, type, anchor, ref)

        yield patch

        with path.open(mode="wb") as fb:
            fb.write(soup.encode("utf-8"))

    def _inv_to_entries(
        self, inv: Mapping[str, Mapping[str, InventoryEntry]]
    ) -> Generator[ParserEntry, None, None]:
        """
        Iterate over a dictionary as returned by our load_inventory object.inv
        parser and yield `ParserEntry`s.
        """
        for type_key, inv_entries in inv.items():
            dash_type = self.convert_type(type_key)
            if dash_type is None:
                continue

            for key, data in inv_entries.items():
                entry = self.create_entry(dash_type, key, data)
                if entry is not None:
                    yield entry

    def convert_type(self, inv_type: str) -> EntryType | None:
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
        self, dash_type: EntryType, key: str, inv_entry: InventoryEntry
    ) -> ParserEntry | None:
        """
        Create a ParserEntry (or None) given inventory details

        Parameters are the dash type, intersphinx inventory key and data tuple.

        This is a method to allow customization by inheritance.
        """
        path_str = inv_entry[0]
        name = inv_entry[1] if inv_entry[1] != "-" else key

        return ParserEntry(name=name, type=dash_type, path=path_str)


def _find_entry_and_add_ref(
    soup: BeautifulSoup, name: str, type: EntryType, anchor: str, ref: str
) -> bool:
    """
    Modify *soup* so Dash can generate TOCs on the fly.
    """
    pos = None
    if type == EntryType.WORD:
        pos = soup.find("dt", id=anchor)
    elif type == EntryType.SECTION:
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
            # mkdocs / mkdocstrings
            or soup.find("a", {"class": "md-nav__link"}, href="#" + anchor)
            # pydoctor
            or soup.find("a", {"name": name})
        )

    if not pos:
        return False

    tag = soup.new_tag("a")
    tag["class"] = "dashAnchor"
    tag["name"] = ref

    pos.insert_before(tag)

    return True
