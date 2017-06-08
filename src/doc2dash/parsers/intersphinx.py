from __future__ import absolute_import, division, print_function

import logging
import os

import attr

from six import iteritems
from sphinx.ext.intersphinx import InventoryFile
from zope.interface import implementer

from . import types
from .utils import (
    APPLE_REF_TEMPLATE,
    IParser,
    ParserEntry,
    has_file_with,
)


log = logging.getLogger(__name__)


INV_TO_TYPE = {
    "attribute": types.ATTRIBUTE,
    "class": types.CLASS,
    "classmethod": types.METHOD,
    "constant": types.CONSTANT,
    "data": types.VALUE,
    "envvar": types.ENV,
    "exception": types.EXCEPTION,
    "function": types.FUNCTION,
    "interface": types.INTERFACE,
    "macro": types.MACRO,
    "member": types.ATTRIBUTE,
    "method": types.METHOD,
    "module": types.PACKAGE,
    "opcode": types.OPCODE,
    "option": types.OPTION,
    "staticmethod": types.METHOD,
    "type": types.TYPE,
    "variable": types.VARIABLE,
    "var": types.VARIABLE,
}


@implementer(IParser)
@attr.s(hash=True)
class InterSphinxParser(object):
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
            for pe in self._inv_to_entries(
                    InventoryFile.load(inv_f, "", os.path.join)
            ):  # this is what Guido gave us `yield from` for :-|
                yield pe

    def _inv_to_entries(self, inv):
        """
        Iterate over a dictionary as returned from Sphinx's object.inv parser
        and yield `ParserEntry`s.
        """
        for type_key, inv_entries in iteritems(inv):
            dash_type = self.convert_type(type_key)
            if dash_type is None:
                continue
            for key, data in iteritems(inv_entries):
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
        except KeyError:
            return

    def create_entry(self, dash_type, key, inv_entry):
        """
        Create a ParserEntry (or None) given inventory details

        Parameters are the dash type, intersphinx inventory key and data tuple
        """
        path_str = inv_entry_to_path(inv_entry)
        return ParserEntry(name=key, type=dash_type, path=path_str)

    def find_and_patch_entry(self, soup, entry):  # pragma: nocover
        return find_and_patch_entry(soup, entry)


def find_and_patch_entry(soup, entry):
    """
    Modify soup so Dash.app can generate TOCs on the fly.
    """
    link = soup.find('a', {'class': 'headerlink'}, href='#' + entry.anchor)
    tag = soup.new_tag('a')
    tag['name'] = APPLE_REF_TEMPLATE.format(entry.type, entry.name)
    if link:
        link.parent.insert(0, tag)
        return True
    elif entry.anchor.startswith('module-'):
        soup.h1.parent.insert(0, tag)
        return True
    else:
        return False


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
