from __future__ import annotations

from pathlib import Path
from typing import ClassVar, Generator, Protocol

import attrs

from bs4 import BeautifulSoup


class Parser(Protocol):
    """
    A *doc2dash* documentation parser.

    Attributes:
        name: The name of this parser. Used in user-facing output.

    """

    name: ClassVar[str] = NotImplemented

    def __init__(self, source: Path):
        """
        Initialize parser.

        Args:
           source: The path to the documentation that will be parsed.
        """

    @staticmethod
    def detect(path: Path) -> bool:
        """
        Check whether *path* can be parsed by this parser.

        Args:
            path: The path to the docset.

        Returns:
            `True`, if the path belongs to this parser.
        """

    @staticmethod
    def guess_name(path: Path) -> str | None:
        """
        Try to guess an appropriate name for a docset.

        Args:
            path: The path to the docset.

        Returns:
            A name, or `None` which means "no idea".
        """

    def parse(self) -> Generator[ParserEntry, None, None]:
        """
        Parse the path that this parser was initialized with and `yield` a
        [`ParserEntry`][doc2dash.parsers.types.ParserEntry] for each
        entry it finds.

        Returns:
            A generator that yields `ParserEntry`s.
        """

    def find_and_patch_entry(
        self, soup: BeautifulSoup, name: str, type: str, anchor: str
    ) -> bool:
        """
        Modify [*soup*](https://beautiful-soup-4.readthedocs.io/en/latest/) so
        Dash.app can generate tables of contents on the fly.

        Args:
            soup: A soup of the file to patch.
            name: The name of the symbol.
            type: One of `doc2dash.parsers.entry_types`.
            anchor: The anchor (`#`) within the file.

        Returns:
            Whether an entry was found and patched.
        """


@attrs.frozen
class ParserEntry:
    """
    A symbol to be indexed, as found by `Parser`'s `parse()` method.
    """

    name: str
    """
    The full display name of the index entry.
    """
    type: str
    """
    The type which is a value from `doc2dash.parsers.entry_types`.
    """
    path: str
    """
    Full path including anchor (`#`). E.g. `api.rst#print`
    """

    def as_tuple(self) -> tuple[str, str, str]:
        """
        Return a tuple of the data for SQL generation.
        """
        return self.name, self.type, self.path
