from __future__ import annotations

import logging
import urllib

from collections import defaultdict
from pathlib import Path
from typing import Any, Callable, Generator

from bs4 import BeautifulSoup
from rich.progress import Progress

from ..output import console
from .types import EntryType, Parser, ParserEntry


log = logging.getLogger(__name__)


def coroutine(func: Callable) -> Callable:  # type: ignore[type-arg]
    def start(*args: Any, **kwargs: Any) -> Any:
        g = func(*args, **kwargs)
        g.__next__()

        return g

    return start


@coroutine
def patch_anchors(
    parser: Parser, docs: Path, show_progressbar: bool
) -> Generator[None, ParserEntry, None]:
    """
    Consume ``ParseEntry``s then patch docs for TOCs by calling
    *parser*'s ``find_entry_and_add_ref``.
    """
    files = defaultdict(list)
    try:
        while True:
            pentry = yield
            try:
                fname, anchor = pentry.path.split("#")
                files[fname].append((pentry.name, pentry.type, anchor))
            except ValueError:
                # pydoctor has no anchors for e.g. classes
                pass
    except GeneratorExit:
        pass

    with Progress(console=console, disable=not show_progressbar) as pbar:
        _patch_files(parser, docs, files, pbar)


def _patch_files(
    parser: Parser,
    docs: Path,
    files: dict[str, list[tuple[str, EntryType, str]]],
    pbar: Progress,
) -> None:
    files_task = pbar.add_task("Patching files for TOCs...", total=len(files))

    for fname, entries in files.items():
        fname = urllib.parse.unquote(fname)
        full_path = docs / fname
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
    parser: Parser,
    fname: str,
    full_path: Path,
    entries: list[tuple[str, EntryType, str]],
) -> BeautifulSoup:
    task = pbar.add_task(f"Patching {fname}...", total=len(entries))
    with full_path.open(encoding="utf-8") as fp:
        soup = BeautifulSoup(fp, "html.parser")
        for (name, type, anchor) in entries:
            if not parser.find_entry_and_add_ref(
                soup,
                name,
                type,
                anchor,
                f"//apple_ref/cpp/{type.value}/{name}",
            ):
                log.debug(
                    "Can't find anchor '%s' (%s) in '%s'.",
                    anchor,
                    type,
                    fname,
                )
            pbar.update(task, advance=1)

    return soup
