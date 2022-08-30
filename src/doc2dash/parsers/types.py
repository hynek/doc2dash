from __future__ import annotations

import abc

from pathlib import Path
from typing import ClassVar, Generator

import attrs

from bs4 import BeautifulSoup


class IParser(metaclass=abc.ABCMeta):
    """
    A doc2dash documentation parser.
    """

    name: ClassVar[str] = NotImplemented
    doc_path: Path = NotImplemented

    def __init__(self, doc_path: Path):
        self.doc_path = doc_path

    @staticmethod
    @abc.abstractmethod
    def detect(path: Path) -> bool:
        """
        A static method that returns whether *path* can be parsed by us.
        """

    @staticmethod
    @abc.abstractmethod
    def guess_name(path: Path) -> str | None:
        """
        Try to guess an appropriate name for the docset.
        """

    @abc.abstractmethod
    def parse(self) -> Generator[ParserEntry, None, None]:
        """
        Parse `self.doc_path`, yield a :class:`ParserEntry` for each found
        entry.
        """

    @abc.abstractmethod
    def find_and_patch_entry(
        self, soup: BeautifulSoup, name: str, type: str, anchor: str
    ) -> bool:
        """
        Modify *soup* so Dash.app can generate TOCs on the fly.

        :param soup: A soup to patch.
        :param name: The name of the symbol.
        :param type: One of `doc2dash.parsers.entry_types`.
        :param anchor: The anchor (`#`) within the file.

        :returns: Whether an entry was found and patched.
        """


@attrs.define(hash=True)
class ParserEntry:
    """
    A symbol as found by the parser that get yielded for further processing.
    """

    name: str
    type: str
    path: str

    def as_tuple(self) -> tuple[str, str, str]:
        """
        Return a tuple of the data for SQL generation.
        """
        return self.name, self.type, self.path
