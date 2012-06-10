import os

from ..helpers import enoent_means_false


HEADER = '''/*
 * searchtools.js
 * ~~~~~~~~~~~~~~
 *
 * Sphinx JavaScript'''


@enoent_means_false
def detect(path):
    """Detect whether *path* is sphinx documentation."""
    with open(os.path.join(path, '_static/searchtools.js')) as f:
        return f.read(len(HEADER)) == HEADER
