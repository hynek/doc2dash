import logging
import os

import attr

from sphinx.ext.intersphinx import InventoryFile

from . import types
from .utils import APPLE_REF_TEMPLATE, IParser, ParserEntry, has_file_with


log = logging.getLogger(__name__)


# https://www.sphinx-doc.org/en/master/usage/restructuredtext/domains.html
# ->
# https://kapeli.com/docsets#supportedentrytypes
INV_TO_TYPE = {
    "attribute": types.ATTRIBUTE,
    "class": types.CLASS,
    "classmethod": types.METHOD,
    "cmdoption": types.OPTION,
    "constant": types.CONSTANT,
    "data": types.VALUE,
    "doc": types.GUIDE,
    "envvar": types.ENV,
    "exception": types.EXCEPTION,
    "function": types.FUNCTION,
    "interface": types.INTERFACE,
    "label": types.SECTION,
    "macro": types.MACRO,
    "member": types.ATTRIBUTE,
    "method": types.METHOD,
    "module": types.PACKAGE,
    "opcode": types.OPCODE,
    "option": types.OPTION,
    "property": types.PROPERTY,
    "protocol": types.PROTOCOL,
    "setting": types.SETTING,
    "staticmethod": types.METHOD,
    "term": types.WORD,
    "type": types.TYPE,
    "variable": types.VARIABLE,
    "var": types.VARIABLE,
}


@attr.s(hash=True)
class InterSphinxParser(IParser):
    """
    Parser for Sphinx-base documentation that generates an objects.inv file for
    the intersphinx extension.
    """

    doc_path = attr.ib()

    name = "intersphinx"

    @staticmethod
    def detect(path):
        return has_file_with(
            path, "objects.inv", b"# Sphinx inventory version 2"
        )

    def parse(self):
        """
        Parse sphinx docs at self.doc_path.

        yield `ParserEntry`s.
        """
        with open(os.path.join(self.doc_path, "objects.inv"), "rb") as inv_f:
            yield from self._inv_to_entries(
                InventoryFile.load(inv_f, "", os.path.join)
            )

    def _inv_to_entries(self, inv):
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

    def convert_type(self, inv_type):
        """
        Map an intersphinx type to a Dash type.

        Returns a Dash type string, or None to not construct entries.
        """
        try:
            return INV_TO_TYPE[inv_type.split(":")[-1]]
        except KeyError:  # pragma: no cover
            log.debug("covert_type: unknown type: %s", inv_type)

            return None

    def create_entry(self, dash_type, key, inv_entry):
        """
        Create a ParserEntry (or None) given inventory details

        Parameters are the dash type, intersphinx inventory key and data tuple
        """
        path_str = inv_entry_to_path(inv_entry)
        name = inv_entry[3] if inv_entry[3] != "-" else key
        return ParserEntry(name=name, type=dash_type, path=path_str)

    def find_and_patch_entry(self, soup, entry):  # pragma: no cover
        return find_and_patch_entry(soup, entry)


def find_and_patch_entry(soup, entry):
    """
    Modify soup so Dash.app can generate TOCs on the fly.
    """
    pos = None
    if entry.type == types.WORD:
        pos = soup.find("dt", id=entry.anchor)
    elif entry.type == types.SECTION:
        pos = soup.find(id=entry.anchor)
    elif entry.anchor.startswith("module-"):
        pos = soup.h1

    if not pos:
        pos = (
            soup.find("a", {"class": "headerlink"}, href="#" + entry.anchor)
            or soup.find(
                "a", {"class": "reference internal"}, href="#" + entry.anchor
            )
            or soup.find("span", id=entry.anchor)
        )

    if not pos:
        return False

    tag = soup.new_tag("a")
    tag["class"] = "dashAnchor"
    tag["name"] = APPLE_REF_TEMPLATE.format(entry.type, entry.name)

    pos.insert_before(tag)

    return True


def inv_entry_to_path(data):
    """
    Determine the path from the intersphinx inventory entry

    Discard the anchors between head and tail to make it
    compatible with situations where extra meta information is encoded.
    """
    path_tuple = data[2].split("#")
    if len(path_tuple) > 1:
        path_str = "#".join((path_tuple[0], path_tuple[-1]))
    else:
        path_str = data[2]
    return path_str
