import argparse
import errno
import logging
import os
import plistlib
import shutil
import sqlite3
import sys

from . import __version__, __doc__, parsers


log = logging.getLogger(__name__)

DEFAULT_DOCSET_PATH = os.path.expanduser(
    '~/Library/Application Support/doc2dash/DocSets'
)


def main():
    """Main cli entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        'source',
        help='Source directory containing API documentation in a supported'
             ' format.'
    )
    parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='force overwriting if destination already exists',
    )
    parser.add_argument(
        '--name', '-n',
        help='name docset explicitly',
    )
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s {}'.format(__version__),
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='limit output to errors and warnings'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='be verbose'
    )
    parser.add_argument(
        '--destination', '-d',
        help='destination directory for docset (default is current), '
             'ignored if -A is specified',
    )
    parser.add_argument(
        '--add-to-dash', '-a',
        action='store_true',
        help='automatically add resulting docset to dash',
    )
    parser.add_argument(
        '-A',
        action='store_true',
        help="create docset in doc2dash's default directory and add resulting "
             "docset to dash",
    )
    parser.add_argument(
        '--icon', '-i',
        help='add PNG icon to docset'
    )
    args = parser.parse_args()

    if args.icon and not args.icon.endswith('.png'):
        print('Please supply a PNG icon.')
        sys.exit(1)

    try:
        level = determine_log_level(args)
        logging.basicConfig(format='%(message)s', level=level)
    except ValueError as e:
        print(e.args[0], '\n')
        parser.print_help()
        sys.exit(1)

    source, dest = setup_paths(args)
    dt = parsers.get_doctype(source)
    if dt is None:
        log.error('"{}" does not contain a known documentation format.'
                  .format(source))
        sys.exit(errno.EINVAL)
    docs, db_conn = prepare_docset(args, dest)
    doc_parser = dt(docs)
    log.info('Converting {} docs from "{}" to "{}".'
             .format(dt.name, source, dest))

    with db_conn:
        log.info('Parsing HTML...')
        toc = doc_parser.add_toc()
        for entry in doc_parser.parse():
            db_conn.execute(
                'INSERT INTO searchIndex VALUES (NULL, ?, ?, ?)',
                entry
            )
            toc.send(entry)
        log.info('Added {0:,} index entries.'.format(
            db_conn.execute('SELECT COUNT(1) FROM searchIndex')
                   .fetchone()[0]))
        log.info('Adding table of contents meta data...')
        toc.close()

    if args.icon:
        add_icon(args.icon, dest)

    if args.add_to_dash:
        log.info('Adding to dash...')
        os.system('open -a dash "{}"'.format(dest))


def determine_log_level(args):
    """We use logging's levels as an easy-to-use verbosity controller."""
    if args.verbose and args.quiet:
        raise ValueError("Supplying both --quiet and --verbose doesn't make "
                         "sense.")
    elif args.verbose:
        level = logging.DEBUG
    elif args.quiet:
        level = logging.ERROR
    else:
        level = logging.INFO
    return level


def setup_paths(args):
    """Determine source and destination using the results of argparse."""
    source = args.source
    if not args.name:
        args.name = os.path.split(source)[-1]
    elif args.name.endswith('.docset'):
        args.name = args.name.replace('.docset', '')
    if args.A:
        args.destination = DEFAULT_DOCSET_PATH
        args.add_to_dash = True
    dest = os.path.join(args.destination or '', args.name + '.docset')
    if not os.path.exists(source):
        log.error('Source directory "{}" does not exist.'.format(source))
        sys.exit(errno.ENOENT)
    if not os.path.isdir(source):
        log.error('Source "{}" is not a directory.'.format(source))
        sys.exit(errno.ENOTDIR)
    dst_exists = os.path.lexists(dest)
    if dst_exists and args.force:
        shutil.rmtree(dest)
    elif dst_exists:
        log.error('Destination path "{}" already exists.'.format(dest))
        sys.exit(errno.EEXIST)
    return source, dest


def prepare_docset(args, dest):
    """Create boilerplate files & directories and copy vanilla docs inside.

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

    plistlib.writePlist(
        {
            'CFBundleIdentifier': args.name,
            'CFBundleName': args.name,
            'DocSetPlatformFamily': args.name.lower(),
            'DashDocSetFamily': 'python',
            'isDashDocset': True,
        },
        os.path.join(dest, 'Contents/Info.plist')
    )

    shutil.copytree(args.source, docs)
    return docs, db_conn


def add_icon(icon, dest):
    """Add icon to docset"""
    shutil.copy2(icon, os.path.join(dest, 'icon.png'))
