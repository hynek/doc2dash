from __future__ import annotations

import errno

from pathlib import Path


def format_ref(type: str, entry: str) -> str:
    """
    Format a reference anchor for *entry* of *type*.
    """
    return f"//apple_ref/cpp/{type}/{entry}"


def has_file_with(path: Path, filename: str, content: bytes) -> bool:
    """
    Check whether *filename* in *path* contains the string *content*.

    *content* is bytes so we can also introspect binary files -- like
    objects.inv.
    """
    try:
        with (path / filename).open("rb") as f:
            return content in f.read()
    except OSError as e:
        if e.errno == errno.ENOENT:
            return False
        else:
            raise
