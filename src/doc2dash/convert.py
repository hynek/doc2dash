# SPDX-FileCopyrightText: 2012 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import logging

from doc2dash.parsers.types import Parser

from .docsets import DocSet
from .parsers.patcher import patch_anchors


log = logging.getLogger(__name__)


def convert_docs(
    *,
    parser: Parser,
    docset: DocSet,
    quiet: bool,
) -> None:
    """
    User *parser* to parse, index, and patch *docset*.
    """
    log.info("Parsing documentation...")
    with docset.db_conn:
        toc = patch_anchors(parser, docset.docs, show_progressbar=not quiet)
        next(toc)

        for entry in parser.parse():
            docset.db_conn.execute(
                "INSERT INTO searchIndex VALUES (NULL, ?, ?, ?)",
                entry.as_tuple(),
            )
            toc.send(entry)

        count = docset.db_conn.execute(
            "SELECT COUNT(1) FROM searchIndex"
        ).fetchone()[0]

    color = "green" if count > 0 else "red"
    log.info(f"Added [{color}]{count:,}[/{color}] index entries.")

    # Now patch for TOCs.
    toc.close()
