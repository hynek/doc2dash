# SPDX-FileCopyrightText: 2012 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import logging
import urllib

from collections import defaultdict
from pathlib import Path
from typing import Generator

from rich.progress import Progress

from ..output import console
from .types import EntryType, Parser, ParserEntry


log = logging.getLogger(__name__)


def patch_anchors(
    parser: Parser, docs: Path, show_progressbar: bool
) -> Generator[None, ParserEntry, None]:
    """
    Consume ``ParseEntry``s then patch docs for TOCs by calling
    *parser*'s ``find_entry_and_add_ref``.
    """
    files = defaultdict(list)
    num = 0
    try:
        while True:
            pentry = yield
            try:
                fname, anchor = pentry.path.split("#")
                files[urllib.parse.unquote(fname)].append(
                    (pentry.name, pentry.type, anchor)
                )
                num += 1
            except ValueError:
                # pydoctor has no anchors for e.g. classes
                pass
    except GeneratorExit:
        pass

    with Progress(console=console, disable=not show_progressbar) as pbar:
        _patch_files(parser, docs, files, num, pbar)


def _patch_files(
    parser: Parser,
    docs: Path,
    files: dict[str, list[tuple[str, EntryType, str]]],
    num: int,
    pbar: Progress,
) -> None:
    entry_task = pbar.add_task("Patching for TOCs...", total=num)
    num_failed = 0
    for fname, entries in files.items():
        with parser.make_patcher_for_file(docs / fname) as patch:
            for name, type, anchor in entries:
                if not patch(
                    name, type, anchor, f"//apple_ref/cpp/{type.value}/{name}"
                ):
                    log.debug(
                        "Can't find anchor '%s' (%s) in '%s'.",
                        anchor,
                        type,
                        fname,
                    )
                    num_failed += 1

                pbar.update(entry_task, advance=1)

    if num_failed:
        log.warning("Failed to add anchors for %s TOC entries.", num_failed)
