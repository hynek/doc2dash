from __future__ import annotations

import codecs
import logging
import os
import urllib

from collections import defaultdict
from typing import Any, Callable, Generator

from bs4 import BeautifulSoup
from rich.progress import Progress

from ..output import console
from .types import IParser, ParserEntry, TOCEntry


log = logging.getLogger(__name__)


def coroutine(func: Callable) -> Callable:  # type: ignore[type-arg]
    def start(*args: Any, **kwargs: Any) -> Any:
        g = func(*args, **kwargs)
        g.__next__()

        return g

    return start


@coroutine
def patch_anchors(
    parser: IParser, show_progressbar: bool
) -> Generator[None, ParserEntry, None]:
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

    with Progress(console=console, disable=not show_progressbar) as pbar:
        _patch_files(parser, files, pbar)


def _patch_files(
    parser: IParser,
    files: dict[str, list[TOCEntry]],
    pbar: Progress,
) -> None:
    files_task = pbar.add_task("Patching files...", total=len(files))

    for fname, entries in files.items():
        fname = urllib.parse.unquote(fname)
        full_path = os.path.join(parser.doc_path, fname)
        try:
            soup = _patch_file(pbar, parser, fname, full_path, entries)
        except FileNotFoundError:
            # This can happen in non-Python Sphinx docs.
            if fname == "py-modindex.html":
                log.warning("Can't open file '%s'. Skipping.", full_path)
            else:
                raise
        else:
            with open(full_path, mode="wb") as fp:
                fp.write(soup.encode("utf-8"))

        pbar.update(files_task, advance=1)


def _patch_file(
    pbar: Progress,
    parser: IParser,
    fname: str,
    full_path: str,
    entries: list[TOCEntry],
) -> BeautifulSoup:
    task = pbar.add_task(f"Patching {fname}...", total=len(entries))
    with codecs.open(full_path, mode="r", encoding="utf-8") as fp:
        soup = BeautifulSoup(fp, "html.parser")
        for entry in entries:
            if not parser.find_and_patch_entry(soup, entry):
                log.debug(
                    "Can't find anchor '%s' (%s) in '%s'.",
                    entry.anchor,
                    entry.type,
                    fname,
                )
            pbar.update(task, advance=1)

    return soup
