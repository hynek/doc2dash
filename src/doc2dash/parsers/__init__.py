from __future__ import annotations

from . import intersphinx, pydoctor
from .types import IParser


DOCTYPES = [pydoctor.PyDoctorParser, intersphinx.InterSphinxParser]


def get_doctype(path: str) -> type[IParser] | None:
    """
    Gets the apropriate doctype for *path*.
    """
    for dt in DOCTYPES:
        if dt.detect(path):
            return dt
    else:
        return None
