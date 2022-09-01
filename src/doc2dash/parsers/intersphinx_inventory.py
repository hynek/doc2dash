"""
Parse Sphinx inventory files so we don't have to rely on Sphinx at runtim
anymore.

Format:

Header:
===
# Sphinx inventory version 2
# Project: Flask
# Version: 0.9-dev
# The remainder of this file is compressed using zlib.
===

Then zlib'ed lines:

name domain:role priority uri display-name

e.g.:

'flask.Blueprint.teardown_request py:method 1 api.html#$ -'

* $ means use name as anchor (i.e. reaplace $ with name)
* `-` means use name as display name
"""

from __future__ import annotations

import re
import zlib

from collections import defaultdict
from typing import IO, Mapping, Tuple


InventoryEntry = Tuple[str, str]  # (uri, display name)


def load_inventory(
    fp: IO[bytes],
) -> Mapping[str, Mapping[str, InventoryEntry]]:
    """
    Load a Sphinx v2 inventory from *fp* and return a mapping of:

    {"role": {"name": ("uri", "display-name"}}
    """
    assert b"# Sphinx inventory version 2\n" == fp.readline()

    key, value = fp.readline().split(b": ", 1)
    assert b"# Project" == key

    key = fp.readline().split(b": ")[0]
    assert b"# Version" == key

    line = fp.readline()
    assert re.fullmatch(
        b"# The (remainder|rest) of this file is compressed (using|with) "
        b"zlib.\n",
        line,
    )

    rv: Mapping[str, dict[str, tuple[str, str]]] = defaultdict(dict)
    for line in zlib.decompress(fp.read()).decode().splitlines():
        name, role, priority, uri, display_name = line.split(" ", 4)
        rv[role][name] = (
            uri.replace("$", name),
            display_name,
        )

    return rv
