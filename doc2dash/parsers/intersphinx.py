from __future__ import absolute_import, division, print_function

import logging
import os

from six import iteritems
from sphinx.ext.intersphinx import read_inventory_v2

from . import types
from .base import _BaseParser
from .sphinx import find_and_patch_entry


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


class InterSphinxParser(_BaseParser):
    """
    Parser for Sphinx-base documentation that generates an objects.inv file for
    the intersphinx extension.
    """
    name = "intersphinx"

    DETECT_FILE = "objects.inv"
    DETECT_PATTERN = b"# Sphinx inventory version 2"

    def parse(self):
        """
        Parse sphinx docs at self.docpath.

        yield tuples of symbol name, type and path
        """
        log.info('Creating database...')
        with open(os.path.join(self.docpath, "objects.inv"), "rb") as inv_f:
            inv_f.readline()  # skip version line that is verified in detection
            for t in _inv_to_elements(
                    read_inventory_v2(inv_f, "", os.path.join)
            ):  # this is what Guido gave us `yield from` for :-|
                yield t

    def find_and_patch_entry(self, soup, entry):  # pragma: nocover
        return find_and_patch_entry(soup, entry)


def _inv_to_elements(inv):
    """
    Iterate over a dictionary as returned from Sphinx's object.inv parser and
    yield `name, type, path` tuples.
    """
    for type_key, val in iteritems(inv):
        try:
            t = INV_TO_TYPE[type_key.split(":")[-1]]
            for el, data in iteritems(val):
                yield el, t, data[2]
        except KeyError:
            pass
