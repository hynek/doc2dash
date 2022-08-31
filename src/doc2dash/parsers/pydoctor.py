from __future__ import annotations

import codecs
import logging
import os

from pathlib import Path
from typing import ClassVar, Generator

import attrs

from bs4 import BeautifulSoup

from .types import ParserEntry
from .utils import format_ref, has_file_with


log = logging.getLogger(__name__)


PYDOCTOR_HEADER = b"""\
        This documentation was automatically generated by
        <a href="https://github.com/twisted/pydoctor/">pydoctor</a>"""

PYDOCTOR_HEADER_OLD = b"""\
      This documentation was automatically generated by
      <a href="https://launchpad.net/pydoctor/">pydoctor</a>"""

PYDOCTOR_HEADER_REALLY_OLD = b"""\
      This documentation was automatically generated by
      <a href="http://codespeak.net/~mwh/pydoctor/">pydoctor</a>"""


@attrs.define
class PyDoctorParser:
    """
    Parser for pydoctor-based documentation: mainly Twisted.
    """

    name: ClassVar[str] = "pydoctor"
    source: Path

    @staticmethod
    def detect(path: Path) -> bool:
        return (
            has_file_with(path, "index.html", PYDOCTOR_HEADER)
            or has_file_with(path, "index.html", PYDOCTOR_HEADER_OLD)
            or has_file_with(path, "index.html", PYDOCTOR_HEADER_REALLY_OLD)
        )

    @staticmethod
    def guess_name(path: Path) -> str | None:
        return None

    def parse(self) -> Generator[ParserEntry, None, None]:
        """
        Parse pydoctor docs at *source*.

        yield `ParserEntry`s
        """
        soup = BeautifulSoup(
            codecs.open(
                os.path.join(self.source, "nameIndex.html"),
                mode="r",
                encoding="utf-8",
            ),
            "html.parser",
        )
        for tag in soup.body.find_all("a"):
            path = tag.get("href")
            data_type = tag.get("data-type")
            if path and data_type and not path.startswith("#"):
                name = tag.string

                yield ParserEntry(
                    name=name,
                    type=data_type.replace("Instance ", ""),
                    path=str(path),
                )

    def find_and_patch_entry(
        self, soup: BeautifulSoup, name: str, type: str, anchor: str
    ) -> bool:
        link = soup.find("a", attrs={"name": anchor})
        if link:
            tag = soup.new_tag("a")
            tag["name"] = format_ref(type, name)
            link.insert_before(tag)

            return True

        return False
