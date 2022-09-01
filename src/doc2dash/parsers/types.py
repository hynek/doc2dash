from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import ClassVar, Generator, Protocol

import attrs

from bs4 import BeautifulSoup


class EntryType(Enum):
    """
    Possible types for entries.

    Pick from <https://kapeli.com/docsets#supportedentrytypes>.
    """

    ATTRIBUTE = "Attribute"
    CLASS = "Class"
    CONSTANT = "Constant"
    ENV = "Environment"
    EXCEPTION = "Exception"
    FUNCTION = "Function"
    GUIDE = "Guide"
    INTERFACE = "Interface"
    MACRO = "Macro"
    METHOD = "Method"
    OPCODE = "Operator"
    OPTION = "Option"
    PACKAGE = "Module"
    PROPERTY = "Property"
    PROTOCOL = "Protocol"
    SECTION = "Section"
    SETTING = "Setting"
    TYPE = "Type"
    VALUE = "Value"
    VARIABLE = "Variable"
    WORD = "Word"


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

        If this parser's `detect()` static method indicates that *source*
        belongs to it, *doc2dash* instantiates it as `parser_type(path)`.

        Args:
           source: The path to the documentation that will be parsed.
        """

    @staticmethod
    def detect(path: Path) -> str | None:
        """
        Check whether *path* can be parsed by this parser.

        Args:
            path: The path to the documentation.

        Returns:
            The name of the documentation or `None` if it's not ours.
        """

    def parse(self) -> Generator[ParserEntry, None, None]:
        """
        Parse the path that this parser was initialized with and `yield` a
        [`ParserEntry`][doc2dash.parsers.types.ParserEntry] for each
        entry it finds.

        Returns:
            A generator that yields `ParserEntry`s.
        """

    def find_entry_and_add_ref(
        self,
        soup: BeautifulSoup,
        name: str,
        type: EntryType,
        anchor: str,
        ref: str,
    ) -> bool:
        """
        Add *ref* next to *anchor* that points to an entry *name* of *type* in
        *soup*.

        Args:
            soup: A [soup](https://beautiful-soup-4.readthedocs.io/) of the
                file to patch.
            name: The name of the entry.
            type: The type of the entry.
            anchor: The anchor (`#`) within the file.
            ref: The ref string to be added to the anchor.

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
    type: EntryType
    """
    The type of the entry.
    """
    path: str
    """
    Full path including anchor (`#`). E.g. `api.rst#print`
    """

    def as_tuple(self) -> tuple[str, str, str]:
        """
        Return a tuple of the data for SQL generation.
        """
        return self.name, self.type.value, self.path
