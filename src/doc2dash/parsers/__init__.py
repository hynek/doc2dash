from __future__ import annotations

from pathlib import Path

from . import intersphinx, pydoctor, types


DOCTYPES: list[type[types.Parser]] = [
    pydoctor.PyDoctorParser,
    intersphinx.InterSphinxParser,
]


def get_doctype(path: Path) -> type[types.Parser] | None:
    """
    Gets the apropriate doctype for *path*.
    """
    for dt in DOCTYPES:
        if dt.detect(path):
            return dt
    else:
        return None


__all__ = ["get_doctype", "types"]
