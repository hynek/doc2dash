# SPDX-FileCopyrightText: 2012 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import errno
import importlib
import logging
import logging.config
import os
import shutil
import subprocess

from importlib import metadata
from pathlib import Path
from typing import Any

import click

from . import docsets, parsers
from .convert import convert_docs
from .output import create_log_config, error_console
from .parsers.types import Parser


log = logging.getLogger(__name__)

DEFAULT_DOCSET_PATH = Path(
    "~/Library/Application Support/doc2dash/DocSets"
).expanduser()
PNG_HEADER = b"\x89PNG\r\n\x1a\n"


class ImportableType(click.ParamType):
    name = "importable"

    def convert(self, value: str, param: Any, ctx: Any) -> Parser:
        path, dot, name = value.rpartition(".")

        if not dot:
            self.fail(f'{value!r} is not an import path: does not contain "."')

        try:
            mod = importlib.import_module(path)
        except ImportError:
            self.fail(f"Could not import module {path!r}")

        try:
            return getattr(mod, name)  # type: ignore[no-any-return]
        except AttributeError:
            self.fail(f"Failed to get attribute {name!r} from module {path!r}")


IMPORTABLE = ImportableType()


@click.command()
@click.argument(
    "source",
    type=click.Path(
        exists=True,
        file_okay=False,
        readable=True,
        resolve_path=True,
        path_type=Path,
    ),
)
@click.option(
    "--name",
    "-n",
    help="Name docset explicitly. If not passed, the parser tries to guess. "
    "If it fails, the directory name of SOURCE is used.",
    metavar="NAME",
)
@click.option(
    "--destination",
    "-d",
    type=click.Path(path_type=Path),
    default=".",
    show_default=True,
    help="Destination directory for docset, ignored if -A is specified.",
)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Force overwriting if destination already exists.",
)
@click.option(
    "--icon",
    "-i",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Add PNG icon to docset.",
)
@click.option(
    "--icon-2x",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Add a 2x-sized PNG icon for hires displays to docset.",
)
@click.option(
    "--index-page",
    "-I",
    metavar="FILENAME",
    type=click.Path(path_type=Path),
    help="Set the file that is shown when the docset is clicked within "
    "Dash relative to the root of SOURCE.",
)
@click.option(
    "--add-to-dash",
    "-a",
    is_flag=True,
    help="Automatically add resulting docset to Dash (works only on macOS).",
)
@click.option(
    "--add-to-global",
    "-A",
    is_flag=True,
    help="Create docset in doc2dash's default global directory "
    f"[{DEFAULT_DOCSET_PATH}] and add it to Dash (works only on macOS).",
)
@click.option(
    "--quiet", "-q", is_flag=True, help="Limit output to errors and warnings."
)
@click.option("--verbose", "-v", is_flag=True, help="Be verbose.")
@click.option(
    "--enable-js",
    "-j",
    is_flag=True,
    help="Enable bundled and external Javascript.",
)
@click.option(
    "--online-redirect-url",
    "-u",
    help="The base URL of the online documentation.",
)
@click.option("--playground-url", help="The URL to a docset playground.")
@click.option(
    "--parser",
    "parser_type",
    type=IMPORTABLE,
    help="The import path of a parser class (e.g. "
    "doc2dash.parsers.intersphinx.InterSphinxParser). Default behavior "
    "is to auto-detect documentation type.",
)
@click.option(
    "--full-text-search",
    type=docsets.FullTextSearch,
    default=docsets.FullTextSearch.OFF,
    help="Whether full-text search should be 'on' or 'off by default. "
    "Or whether it's 'forbidden' to switch it on by the user at all.",
)
@click.version_option(version=metadata.version("doc2dash"))
def main(
    source: Path,
    force: bool,
    name: str | None,
    quiet: bool,
    verbose: bool,
    destination: Path,
    add_to_dash: bool,
    add_to_global: bool,
    icon: Path | None,
    icon_2x: Path | None,
    index_page: Path | None,
    enable_js: bool,
    online_redirect_url: str | None,
    playground_url: str | None,
    parser_type: type[Parser] | None,
    full_text_search: docsets.FullTextSearch,
) -> None:
    """
    Convert docs from SOURCE to Dash's docset format.
    """
    if verbose and quiet:
        error_console.print(
            "Passing both --quiet and --verbose makes no sense."
        )
        raise SystemExit(1)

    logging.config.dictConfig(create_log_config(verbose=verbose, quiet=quiet))

    if icon:
        with icon.open("rb") as f:
            header = f.read(len(PNG_HEADER))

        if header != PNG_HEADER:
            log.error(
                '"%s" is not a valid PNG image.',
                icon.name,
            )
            raise SystemExit(errno.EINVAL)

    if index_page and not (source / index_page).exists():
        log.error(
            'Index page "%s" does not exist within "%s".',
            index_page,
            source,
        )
        raise SystemExit(errno.ENOENT)

    if parser_type is None:
        parser_type, detected_name = parsers.get_doctype(source)
        if not (detected_name and parser_type):
            log.error(
                '"%s" does not contain a known documentation format.', source
            )
            raise SystemExit(errno.EINVAL)
    else:
        detected_name = parser_type.detect(source)
        if not detected_name:
            log.error(
                "Supplied parser %r can't parse '%s'.", parser_type, source
            )
            raise SystemExit(errno.EINVAL)

    if name is None:
        name = detected_name

    dest = setup_destination(
        destination,
        name,
        add_to_global=add_to_global,
        force=force,
    )
    docset = docsets.prepare_docset(
        source,
        dest,
        name,
        index_page,
        enable_js,
        online_redirect_url,
        playground_url,
        icon,
        icon_2x,
        full_text_search,
    )

    parser = parser_type(docset.docs)

    log.info(
        "Converting [b]%s[/b] docs from '%s' to '%s'.",
        parser.name,
        source,
        dest,
    )

    convert_docs(parser=parser, docset=docset, quiet=quiet)

    if add_to_dash or add_to_global:
        log.info("Adding to Dash...")
        subprocess.check_output(("open", "-a", "dash", dest))  # noqa: S603


def setup_destination(
    destination: Path,
    name: str,
    add_to_global: bool,
    force: bool,
) -> Path:
    """
    Determine source and destination using the options.
    """
    if add_to_global:
        destination = DEFAULT_DOCSET_PATH

    dest = (destination / name).with_suffix(".docset")
    dst_exists = os.path.lexists(dest)
    if dst_exists and force:
        shutil.rmtree(dest)
    elif dst_exists:
        log.error('Destination path "%s" already exists.', dest)

        raise SystemExit(errno.EEXIST)

    return dest


if __name__ == "__main__":
    main()
