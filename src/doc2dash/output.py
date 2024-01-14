# SPDX-FileCopyrightText: 2012 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import logging

from typing import ClassVar

from rich.console import Console


console = Console(soft_wrap=True)
error_console = Console(stderr=True, style="bold red", soft_wrap=True)


class RichEchoHandler(logging.Handler):
    """
    Use rich.echo() for logging.  Has the advantage of stripping color codes
    if output is redirected.  Also is generally more predictable.
    """

    _level_to_fg: ClassVar[dict[int, str]] = {
        logging.ERROR: "red",
        logging.WARN: "yellow",
    }

    def emit(self, record: logging.LogRecord) -> None:
        if record.levelno > logging.WARN:  # noqa: SIM108
            print = error_console.print
        else:
            print = console.print

        print(
            record.getMessage(),
            style=self._level_to_fg.get(record.levelno, "reset"),
        )


def create_log_config(verbose: bool, quiet: bool) -> dict[str, object]:
    """
    We use logging's levels as an easy-to-use verbosity controller.
    """
    assert not (verbose and quiet)
    if verbose:
        level = logging.DEBUG
    elif quiet:
        level = logging.ERROR
    else:
        level = logging.INFO

    logger_cfg = {"handlers": ["rich_handler"], "level": level}

    return {
        "version": 1,
        "formatters": {"rich_formatter": {"format": "%(message)s"}},
        "handlers": {
            "rich_handler": {
                "level": level,
                "class": "doc2dash.output.RichEchoHandler",
                "formatter": "rich_formatter",
            }
        },
        "loggers": {"doc2dash": logger_cfg, "__main__": logger_cfg},
    }
