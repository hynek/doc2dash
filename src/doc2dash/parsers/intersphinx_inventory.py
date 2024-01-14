# SPDX-FileCopyrightText: 2012 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

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

import logging
import re
import zlib

from collections import defaultdict
from pathlib import Path
from typing import Callable, Mapping, Tuple

import attrs


log = logging.getLogger(__name__)


InventoryEntry = Tuple[str, str]  # (uri, display name)


def load_inventory(source: Path) -> Mapping[str, Mapping[str, InventoryEntry]]:
    """
    Load a Sphinx v2 inventory from *fp* and return a mapping of:

    {"role": {"name": ("path#anchor", "display-name"}}
    """
    with (source / "objects.inv").open("rb") as fp:
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

        entries = zlib.decompress(fp.read()).decode().splitlines()

    return _lines_to_tuples(CachedFileExists(source), entries)


# This regular expression is straight from Sphinx:
# https://github.com/sphinx-doc/sphinx/blob/5e9550c78e3421dd7dcab037021d996841178f67/sphinx/util/inventory.py#L115
# Only modified to not capture priority that we don't care about.
_match_inv_line = re.compile(
    r"(?x)(.+?)\s+(\S+)\s+(?:-?\d+)\s+?(\S*)\s+(.*)"
).match


def _lines_to_tuples(
    check_exists: Callable[[str], bool], entries: list[str]
) -> Mapping[str, dict[str, tuple[str, str]]]:
    """
    Transform inventory lines *entries* to the required dict of dicts of
    tuples.

    Use *check_exists* callable to verify whether the indexed path exits at
    all.
    """
    rv: Mapping[str, dict[str, tuple[str, str]]] = defaultdict(dict)

    for line in entries:
        m = _match_inv_line(line.rstrip())
        if not m:
            log.warning("intersphinx: invalid line: %r. Skipping.", line)
            continue

        name, role, uri, display_name = m.groups()
        path, uri = _clean_up_path(uri.replace("$", name))

        if not check_exists(path):
            continue

        rv[role][name] = (uri, display_name)

    return rv


@attrs.define
class CachedFileExists:
    base: Path
    _exists: set[str] = attrs.Factory(set)
    _missing: set[str] = attrs.Factory(set)

    def __call__(self, path: str) -> bool:
        if path in self._exists:
            return True

        if path in self._missing:
            return False

        if Path(self.base / path).exists():
            self._exists.add(path)

            return True

        self._missing.add(path)

        # Moving it here ensures we log only once about each file.
        log.warning(
            "intersphinx: path '%s' is in objects.inv, but does not exist."
            " Skipping.",
            path,
        )

        return False


def _clean_up_path(uri: str) -> tuple[str, str]:
    """
    Clean up a path as it comes from an inventory.

    Discard the anchors between head and tail to make it
    compatible with situations where extra meta information is encoded.

    If the path ends with an "/", append an index.html.

    Returns:
        tuple of cleaned up path / URI based on cleaned up path
    """
    path_tuple = uri.split("#")
    if len(path_tuple) > 1:
        # Throw away everything between path and last anchor.
        path = _maybe_index(path_tuple[0])
        return path, f"{path}#{path_tuple[-1]}"

    # No anchor: path = URI
    path = _maybe_index(uri)
    return path, path


def _maybe_index(path: str) -> str:
    if path.endswith("/"):
        return f"{path}index.html"

    return path
