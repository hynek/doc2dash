from __future__ import annotations

from doc2dash.parsers.types import EntryType


def format_ref(type: EntryType, entry: str) -> str:
    """
    Format a reference anchor for *entry* of *type*.
    """
    return f"//apple_ref/cpp/{type.value}/{entry}"
