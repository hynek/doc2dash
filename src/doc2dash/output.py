from __future__ import annotations

import logging

from typing import Any

import click


class ClickEchoHandler(logging.Handler):
    """
    Use click.echo() for logging.  Has the advantage of stripping color codes
    if output is redirected.  Also is generally more predictable.
    """

    _level_to_fg = {logging.ERROR: "red", logging.WARN: "yellow"}

    def emit(self, record: logging.LogRecord) -> None:
        click.echo(
            click.style(
                record.getMessage(),
                fg=self._level_to_fg.get(record.levelno, "reset"),
            ),
            err=record.levelno >= logging.WARN,
        )


def create_log_config(verbose: bool, quiet: bool) -> dict[str, Any]:
    """
    We use logging's levels as an easy-to-use verbosity controller.
    """
    if verbose and quiet:
        raise ValueError(
            "Supplying both --quiet and --verbose makes no sense."
        )
    elif verbose:
        level = logging.DEBUG
    elif quiet:
        level = logging.ERROR
    else:
        level = logging.INFO

    logger_cfg = {"handlers": ["click_handler"], "level": level}

    return {
        "version": 1,
        "formatters": {"click_formatter": {"format": "%(message)s"}},
        "handlers": {
            "click_handler": {
                "level": level,
                "class": "doc2dash.output.ClickEchoHandler",
                "formatter": "click_formatter",
            }
        },
        "loggers": {"doc2dash": logger_cfg, "__main__": logger_cfg},
    }
