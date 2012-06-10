import argparse
import errno
import os
import plistlib
import shutil
import sqlite3
import sys

from . import __version__, __doc__, parsers


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
            '--version',
            action='version',
            version='%(prog)s {}'.format(__version__),
    )
    args = parser.parse_args()

    source, dest = setup_paths(args)
    dt = parsers.get_doctype(source)
    if dt is None:
        print('"{}" does not contain a known documentation format.'
              .format(source))
        sys.exit(errno.EINVAL)
    print('Converting {} docs from {} to {}.'.format(dt.name, source, dest))
    resources, docs = prepare_docset(args, dest)
    # 4. index files


def setup_paths(args):
    """Determine source and destination using the results of argparse."""
    source = args.source
    dest = os.path.split(source)[-1] + '.docset'
    if not os.path.exists(source):
        print('Source directory "{}" does not exist.'.format(source))
        sys.exit(errno.ENOENT)
    if not os.path.isdir(source):
        print('Source "{}" is not a directory.'.format(source))
        sys.exit(errno.ENOTDIR)
    dst_exists = os.path.lexists(dest)
    if dst_exists and args.force:
        shutil.rmtree(dest)
    elif dst_exists:
        print('Destination path "{}" already exists.'.format(dest))
        sys.exit(errno.EEXIST)
    return source, dest


def prepare_docset(args, dest):
    """Create boilerplate files & directories and copy vanilla docs inside.

    Return a tuple of path to resources and connection to sqlite db.

    """
    name = os.path.split(args.source)[-1]
    resources = os.path.join(dest, 'Contents/Resources/')
    docs = os.path.join(resources, 'Documents')
    os.makedirs(docs)

    with sqlite3.connect(os.path.join(resources, 'docSet.dsidx')) as db_conn:
        db_conn.execute(
                'CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, '
                'type TEXT, path TEXT)'
        )

    plistlib.writePlist(
            {
                'CFBundleIdentifier': name,
                'CFBundleName': name,
                'DocSetPlatformFamily': name,
                'isDashDocset': True,
            },
            os.path.join(dest, 'Contents/Info.plist')
    )

    shutil.copytree(args.source, os.path.join(docs, 'data'))
    return resources, db_conn
