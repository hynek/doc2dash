# SPDX-FileCopyrightText: 2012 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from pathlib import Path

from . import intersphinx, types


DOCTYPES: list[type[types.Parser]] = [
    intersphinx.InterSphinxParser,
]


def get_doctype(
    path: Path,
) -> tuple[type[types.Parser], str] | tuple[None, None]:
    """
    Gets the appropriate doctype for *path*.

    Returns:
        Tuple of parser type and the name of the documentation.
    """
    for dt in DOCTYPES:
        name = dt.detect(path)
        if name:
            return dt, name
    else:
        return None, None


__all__ = ["get_doctype", "types"]
