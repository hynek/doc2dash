import abc
import codecs
import errno
import logging
import os
import urllib

from collections import defaultdict

import attr
import click

from bs4 import BeautifulSoup


log = logging.getLogger(__name__)


@attr.s(hash=True)
class TOCEntry:
    """
    A symbol entry generated by the parser and to be added to the TOC.
    """

    name = attr.ib(validator=attr.validators.instance_of(str))
    type = attr.ib(validator=attr.validators.instance_of(str))
    anchor = attr.ib(validator=attr.validators.instance_of(str))


class IParser(metaclass=abc.ABCMeta):
    """
    A doc2dash documentation parser.
    """

    name: str = NotImplemented
    doc_path: str = NotImplemented

    def detect(path: str) -> bool:
        """
        A static method that returns whether *path* can be parsed by us.
        """

    def parse() -> None:
        """
        Parse `self.doc_path`, yield a :class:`ParserEntry` for each found
        entry.
        """

    def find_and_patch_entry(soup: BeautifulSoup, entry: TOCEntry) -> None:
        """
        Modify *soup* so Dash.app can generate TOCs on the fly.

        :param soup: A soup to patch.
        :type soup: bs4.BeautifulSoup
        :param entry: A table of contents entry that has to be patched.
        :type entry: TOCEntry
        """


@attr.s(hash=True)
class ParserEntry:
    """
    A symbol as found by the parser that get yield for further processing.
    """

    name = attr.ib(validator=attr.validators.instance_of(str))
    type = attr.ib(validator=attr.validators.instance_of(str))
    path = attr.ib(validator=attr.validators.instance_of(str))

    def as_tuple(self):
        """
        Return a tuple of the data for SQL generation.
        """
        return self.name, self.type, self.path


def coroutine(func):
    def start(*args, **kwargs):
        g = func(*args, **kwargs)
        g.__next__()
        return g

    return start


APPLE_REF_TEMPLATE = "//apple_ref/cpp/{}/{}"


@coroutine
def patch_anchors(parser, show_progressbar):
    """
    Consume ``ParseEntry``s then patch docs for TOCs by calling
    *parser*'s ``find_and_patch_entry``.
    """
    files = defaultdict(list)
    try:
        while True:
            pentry = yield
            try:
                fname, anchor = pentry.path.split("#")
                files[fname].append(
                    TOCEntry(name=pentry.name, type=pentry.type, anchor=anchor)
                )
            except ValueError:
                # pydoctor has no anchors for e.g. classes
                pass
    except GeneratorExit:
        pass

    def patch_files(files):
        for fname, entries in files:
            full_path = urllib.parse.unquote(os.path.join(parser.doc_path, fname))
            with codecs.open(full_path, mode="r", encoding="utf-8") as fp:
                soup = BeautifulSoup(fp, "html.parser")
                for entry in entries:
                    if not parser.find_and_patch_entry(soup, entry):
                        log.debug(
                            "Can't find anchor '%s' (%s) in %s.",
                            entry.anchor,
                            entry.type,
                            click.format_filename(fname),
                        )
            with open(full_path, mode="wb") as fp:
                fp.write(soup.encode("utf-8"))

    if show_progressbar is True:
        with click.progressbar(
            files.items(),
            width=0,
            length=len(files),
            label="Adding table of contents meta data...",
        ) as pbar:
            patch_files(pbar)
    else:
        patch_files(files.items())


def has_file_with(path, filename, content):
    """
    Check whether *filename* in *path* contains the string *content*.
    """
    try:
        with open(os.path.join(path, filename), "rb") as f:
            return content in f.read()
    except OSError as e:
        if e.errno == errno.ENOENT:
            return False
        else:
            raise
