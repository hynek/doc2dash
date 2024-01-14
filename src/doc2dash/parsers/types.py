# SPDX-FileCopyrightText: 2012 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from contextlib import contextmanager
from enum import Enum
from pathlib import Path
from typing import ClassVar, Generator, Iterator, Protocol

import attrs


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

    @contextmanager
    def make_patcher_for_file(self, path: Path) -> Iterator[Patcher]:
        """
        A context manager that prepares for patching *path* and returns a
        `Patcher` callable.

        Args:
            path: path to file to patch

        Yields:
            A patch function.
        """


class Patcher(Protocol):
    """
    A callable that patches the file that it belongs to and returns whether it
    did.
    """

    def __call__(
        self, name: str, type: EntryType, anchor: str, ref: str
    ) -> bool:
        """
        Args:
            name: name of the entry
            type: the type of the entry
            anchor: the place to add *ref*
            ref: the reference to add before *anchor*

        Returns:
            Whether it found the anchor and did anything.
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
