from __future__ import annotations

import errno
import importlib
import logging
import logging.config
import os
import shutil

from importlib import metadata

import click

from . import docsets, parsers
from .output import create_log_config
from .parsers.patcher import patch_anchors


log = logging.getLogger(__name__)

DEFAULT_DOCSET_PATH = os.path.expanduser(
    "~/Library/Application Support/doc2dash/DocSets"
)
PNG_HEADER = b"\x89PNG\r\n\x1a\n"


class ImportableType(click.ParamType):
    name = "importable"

    def convert(self, value, param, ctx):
        path, dot, name = value.rpartition(".")

        if not dot:
            self.fail(f'{value!r} is not an import path: does not contain "."')

        try:
            mod = importlib.import_module(path)
        except ImportError:
            self.fail(f"Could not import module {path!r}")
        try:
            return getattr(mod, name)
        except AttributeError:
            self.fail(f"Failed to get attribute {name!r} from module {path!r}")


IMPORTABLE = ImportableType()


@click.command()
@click.argument(
    "source",
    type=click.Path(
        exists=True, file_okay=False, readable=True, resolve_path=True
    ),
)
@click.option("--name", "-n", help="Name docset explicitly.", metavar="NAME")
@click.option(
    "--destination",
    "-d",
    type=click.Path(),
    default=".",
    show_default=True,
    help="Destination directory for docset, ignored if " "-A is specified.",
)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Force overwriting if destination already exists.",
)
@click.option(
    "--icon", "-i", type=click.File("rb"), help="Add PNG icon to docset."
)
@click.option(
    "--index-page",
    "-I",
    metavar="FILENAME",
    type=click.Path(),
    help="Set the file that is shown when the docset is clicked within "
    "Dash.app.",
)
@click.option(
    "--add-to-dash",
    "-a",
    is_flag=True,
    help="Automatically add resulting docset to Dash.app.",
)
@click.option(
    "--add-to-global",
    "-A",
    is_flag=True,
    help="Create docset in doc2dash's default global directory [{}] "
    "and add it to Dash.app (works only on macOS).".format(
        click.format_filename(DEFAULT_DOCSET_PATH)
    ),
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
    default=None,
    help="The base URL of the online documentation.",
)
@click.option(
    "--parser",
    default=None,
    type=IMPORTABLE,
    help="The import path of a parser class (e.g. "
    "doc2dash.parsers.intersphinx.InterSphinxParser). Default behavior "
    "is to auto-detect documentation type.",
)
@click.version_option(version=metadata.version("doc2dash"))
def main(
    source,
    force,
    name,
    quiet,
    verbose,
    destination,
    add_to_dash,
    add_to_global,
    icon,
    index_page,
    enable_js,
    online_redirect_url,
    parser,
):
    """
    Convert docs from SOURCE to Dash.app's docset format.
    """
    try:
        logging.config.dictConfig(
            create_log_config(verbose=verbose, quiet=quiet)
        )
    except ValueError as e:
        click.secho(e.args[0], fg="red")
        raise SystemExit(1)

    if icon:
        icon_data = icon.read()
        if not icon_data.startswith(PNG_HEADER):
            log.error(
                '"%s" is not a valid PNG image.',
                click.format_filename(icon.name),
            )
            raise SystemExit(1)
    else:
        icon_data = None

    source, dest, name = setup_paths(
        source,
        destination,
        name=name,
        add_to_global=add_to_global,
        force=force,
    )
    if parser is None:
        parser = parsers.get_doctype(source)
        if parser is None:
            log.error(
                '"{}" does not contain a known documentation format.'.format(
                    click.format_filename(source)
                )
            )
            raise SystemExit(errno.EINVAL)
    docset = docsets.prepare_docset(
        source, dest, name, index_page, enable_js, online_redirect_url
    )
    doc_parser = parser(doc_path=docset.docs)
    log.info(
        (
            "Converting "
            + click.style("{parser_name}", bold=True)
            + ' docs from "{src}" to "{dst}".'
        ).format(
            parser_name=parser.name,
            src=click.format_filename(source, shorten=True),
            dst=click.format_filename(dest),
        )
    )

    with docset.db_conn:
        log.info("Parsing documentation...")
        toc = patch_anchors(doc_parser, show_progressbar=not quiet)
        for entry in doc_parser.parse():
            docset.db_conn.execute(
                "INSERT INTO searchIndex VALUES (NULL, ?, ?, ?)",
                entry.as_tuple(),
            )
            toc.send(entry)
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
        toc.close()

    if icon_data:
        docsets.add_icon(icon_data, dest)

    if add_to_dash or add_to_global:
        log.info("Adding to Dash.app...")
        os.system(f'open -a dash "{dest}"')


def setup_paths(source, destination, name, add_to_global, force):
    """
    Determine source and destination using the options.
    """
    if source[-1] == "/":
        source = source[:-1]
    if not name:
        name = os.path.split(source)[-1]
    elif name.endswith(".docset"):
        name = name.replace(".docset", "")
    if add_to_global:
        destination = DEFAULT_DOCSET_PATH
    dest = os.path.join(destination or "", name + ".docset")
    dst_exists = os.path.lexists(dest)
    if dst_exists and force:
        shutil.rmtree(dest)
    elif dst_exists:
        log.error(
            f'Destination path "{click.format_filename(dest)}" already exists.'
        )
        raise SystemExit(errno.EEXIST)

    return source, dest, name


if __name__ == "__main__":
    main()
