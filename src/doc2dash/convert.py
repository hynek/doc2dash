from __future__ import annotations

import logging

import click

from doc2dash.parsers.types import IParser

from .docsets import DocSet
from .parsers.patcher import patch_anchors


log = logging.getLogger(__name__)


def convert_docs(
    *,
    parser: IParser,
    docset: DocSet,
    quiet: bool,
) -> None:
    log.info("Parsing documentation...")
    with docset.db_conn:
        toc = patch_anchors(parser, show_progressbar=not quiet)

        for entry in parser.parse():
            docset.db_conn.execute(
                "INSERT INTO searchIndex VALUES (NULL, ?, ?, ?)",
                entry.as_tuple(),
            )
            toc.send(entry)

        toc.close()

        count = docset.db_conn.execute(
            "SELECT COUNT(1) FROM searchIndex"
        ).fetchone()[0]

    log.info(
        (
            "Added "
            + click.style("{count:,}", fg="green" if count > 0 else "red")
            + " index entries."
        ).format(count=count)
    )
