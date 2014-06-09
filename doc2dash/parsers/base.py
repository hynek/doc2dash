import errno
import logging
import os
import sys

from collections import defaultdict, namedtuple

from bs4 import BeautifulSoup


log = logging.getLogger(__name__)


Entry = namedtuple('Entry', ['name', 'type', 'anchor'])


if sys.version_info.major > 2:
    def coroutine(func):
        def start(*args, **kwargs):
            g = func(*args, **kwargs)
            g.__next__()
            return g
        return start
else:
    def coroutine(func):
        def start(*args, **kwargs):
            g = func(*args, **kwargs)
            g.next()
            return g
        return start


class _BaseParser(object):
    """
    Abstract parser base class.
    """
    APPLE_REF = '//apple_ref/cpp/{}/{}'

    def __init__(self, docpath):
        self.docpath = docpath

    @classmethod
    def detect(cl, path):
        """
        Detect whether *path* is documentation of the type of the class
        that sub-classes _BaseParser.  This is ugly and should be replaced by
        composition eventually.

        Until then, sub-classes need to set class-attributes DETECT_FILE with
        a file name to check and DETECT_PATTERN that has to be contained within
        that file.
        """
        try:
            with open(os.path.join(path, cl.DETECT_FILE)) as f:
                return cl.DETECT_PATTERN in f.read()
        except IOError as e:
            if e.errno == errno.ENOENT:
                return False
            else:
                raise

    @coroutine
    def add_toc(self):
        """
        Consume tuples as returned by parse(), then patch docs for TOCs.
        """
        files = defaultdict(list)
        try:
            while True:
                entry = (yield)
                try:
                    fname, anchor = entry[2].split('#')
                    files[fname].append(
                        Entry(entry[0], entry[1], anchor)
                    )
                except ValueError:
                    # pydoctor has no anchors for e.g. classes
                    pass
        except GeneratorExit:
            pass

        for fname, entries in files.items():
            full_path = os.path.join(self.docpath, fname)
            with open(full_path) as fp:
                soup = BeautifulSoup(fp, 'lxml')
                for entry in entries:
                    if not self.find_and_patch_entry(soup, entry):
                        log.debug("Can't find anchor {} in {}."
                                  .format(entry.anchor, fname))
            with open(full_path, 'w') as fp:
                fp.write(str(soup))
