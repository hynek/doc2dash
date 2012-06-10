import argparse
import errno
import os
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
            '--version',
            action='version',
            version='%(prog)s {}'.format(__version__),
    )
    args = parser.parse_args()

    source, dest = setup_paths(args)
    # 1. detect type
    dt = parsers.get_doctype(source)
    if dt is None:
        print('"{}" does not contain a known documentation format.'
              .format(source))
        sys.exit(errno.EINVAL)

    print('Converting {} docs from {} to {}.'.format(dt.name, source, dest))
    # 2. create boilerplate
    # 3. copy files
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
    if os.path.lexists(dest):
        print('Destination path "{}" already exists.'.format(dest))
        sys.exit(errno.EEXIST)
    return source, dest
