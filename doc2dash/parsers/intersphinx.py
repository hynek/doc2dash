from __future__ import absolute_import, division, print_function

import logging
import os

from characteristic import attributes
from six import iteritems
from sphinx.ext.intersphinx import read_inventory_v2
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
@attributes(["doc_path"])
class InterSphinxParser(object):
    """
    Parser for Sphinx-base documentation that generates an objects.inv file for
    the intersphinx extension.
    """
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
            inv_f.readline()  # skip version line that is verified in detection
            for pe in _inv_to_entries(
                    read_inventory_v2(inv_f, "", os.path.join)
            ):  # this is what Guido gave us `yield from` for :-|
                yield pe

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


def _inv_to_entries(inv):
    """
    Iterate over a dictionary as returned from Sphinx's object.inv parser and
    yield `ParserEntry`s.
    """
    for type_key, val in iteritems(inv):
        try:
            t = INV_TO_TYPE[type_key.split(":")[-1]]
            for el, data in iteritems(val):
                yield ParserEntry(name=el, type=t, path=data[2])
        except KeyError:
            pass
