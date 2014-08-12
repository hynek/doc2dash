from __future__ import absolute_import, division, print_function

import errno
import logging
import os
import plistlib
import shutil
import sqlite3

import click

from . import __version__, parsers


log = logging.getLogger(__name__)

DEFAULT_DOCSET_PATH = os.path.expanduser(
    '~/Library/Application Support/doc2dash/DocSets'
)
PNG_HEADER = b"\x89PNG\r\n\x1a\n"


@click.command()
@click.argument("source",
                type=click.Path(exists=True, file_okay=False, readable=True))
@click.option(
    "--force", "-f", is_flag=True, default=False,
    help="force overwriting if destination already exists")
@click.option("--name", "-n", help="name docset explicitly", metavar="NAME")
@click.option(
    "--quiet", "-q", is_flag=True, default=False,
    help="limit output to errors and warnings"
)
@click.option(
    "--verbose", "-v", is_flag=True, default=False,
    help="be verbose"
)
@click.option(
    "--destination", "-d", type=click.Path(), default=".", show_default=True,
    help="destination directory for docset, ignored if "
    "-A is specified"
)
@click.option(
    "--add-to-dash", "-a", is_flag=True, default=False,
    help="automatically add resulting docset to Dash.app"
)
@click.option(
    "--add-to-global", "-A", is_flag=True, default=False,
    help="create docset in doc2dash's default global directory [{}] "
    "and add it to Dash.app".format(DEFAULT_DOCSET_PATH)
)
@click.option(
    "--icon", "-i", type=click.File("rb"),
    help="add PNG icon to docset"
)
@click.option(
    "--index-page", "-I", metavar="FILENAME",
    help="set the file that is shown when the docset is clicked within "
    "Dash.app"
)
@click.version_option(version=__version__)
def main(source, force, name, quiet, verbose, destination, add_to_dash,
         add_to_global, icon, index_page):
    """
    Convert docs from SOURCE to Dash.app's docset format.
    """
    if icon:
        icon_data = icon.read()
        if not icon_data.startswith(PNG_HEADER):
            print("The supplied icon is not a valid PNG image.")
            raise SystemExit(1)
    else:
        icon_data = None

    try:
        level = determine_log_level(verbose=verbose, quiet=quiet)
    except ValueError as e:
        click.echo(e.args[0] + '\n')
        raise SystemExit(1)
    logging.basicConfig(format='%(message)s', level=level)

    source, dest, name = setup_paths(
        source, destination, name=name, add_to_global=add_to_global,
        force=force
    )
    dt = parsers.get_doctype(source)
    if dt is None:
        log.error(
            click.style('"{}" does not contain a known documentation format.'
                        .format(source), fg="red")
        )
        raise SystemExit(errno.EINVAL)
    docs, db_conn = prepare_docset(source, dest, name, index_page)
    doc_parser = dt(docs)
    log.info(('Converting ' + click.style('{parser_name}', bold=True) +
              ' docs from "{src}" to "{dst}".')
             .format(parser_name=dt.name, src=source, dst=dest))

    with db_conn:
        log.info('Parsing HTML...')
        toc = doc_parser.add_toc()
        for entry in doc_parser.parse():
            db_conn.execute(
                'INSERT INTO searchIndex VALUES (NULL, ?, ?, ?)',
                entry
            )
            toc.send(entry)
        count = (db_conn.execute('SELECT COUNT(1) FROM searchIndex')
                 .fetchone()[0])
        log.info(('Added ' +
                  click.style('{count:,}',
                              fg="green" if count > 0 else "red") +
                  ' index entries.')
                 .format(count=count))
        log.info('Adding table of contents meta data...')
        toc.close()

    if icon_data:
        add_icon(icon_data, dest)

    if add_to_dash or add_to_global:
        log.info('Adding to dash...')
        os.system('open -a dash "{}"'.format(dest))


def determine_log_level(verbose, quiet):
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
    return level


def setup_paths(source, destination, name, add_to_global, force):
    """
    Determine source and destination using the options.
    """
    if source[-1] == "/":
        source = source[:-1]
    if not name:
        name = os.path.split(source)[-1]
    elif name.endswith('.docset'):
        name = name.replace('.docset', '')
    if add_to_global:
        destination = DEFAULT_DOCSET_PATH
    dest = os.path.join(destination or '', name + '.docset')
    dst_exists = os.path.lexists(dest)
    if dst_exists and force:
        shutil.rmtree(dest)
    elif dst_exists:
        log.error('Destination path "{}" already exists.'.format(dest))
        raise SystemExit(errno.EEXIST)
    return source, dest, name


def prepare_docset(source, dest, name, index_page):
    """
    Create boilerplate files & directories and copy vanilla docs inside.

    Return a tuple of path to resources and connection to sqlite db.
    """
    resources = os.path.join(dest, 'Contents/Resources/')
    docs = os.path.join(resources, 'Documents')
    os.makedirs(resources)

    db_conn = sqlite3.connect(os.path.join(resources, 'docSet.dsidx'))
    db_conn.row_factory = sqlite3.Row
    db_conn.execute(
        'CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, '
        'type TEXT, path TEXT)'
    )
    db_conn.commit()

    plist_cfg = {
        'CFBundleIdentifier': name,
        'CFBundleName': name,
        'DocSetPlatformFamily': name.lower(),
        'DashDocSetFamily': 'python',
        'isDashDocset': True,
    }
    if index_page is not None:
        plist_cfg['dashIndexFilePath'] = index_page

    plistlib.writePlist(
        plist_cfg,
        os.path.join(dest, 'Contents/Info.plist')
    )

    shutil.copytree(source, docs)
    return docs, db_conn


def add_icon(icon_data, dest):
    """
    Add icon to docset
    """
    with open(os.path.join(dest, 'icon.png'), "wb") as f:
        f.write(icon_data)
