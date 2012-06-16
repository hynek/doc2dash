import os

from bs4 import BeautifulSoup

from doc2dash.parsers.types import CLASS, PACKAGE, METHOD


def parse(docpath):
    """Parse pydoctor docs at *docpath*.

    yield tuples of symbol name, type and path

    """
    soup = BeautifulSoup(open(os.path.join(docpath, 'nameIndex.html')), 'lxml')
    print('Creating database...')
    for tag in soup.body.find_all('a'):
        path = tag.get('href')
        if path and not path.startswith('#'):
            name = tag.string
            yield name, _guess_type(name, path), path


def _guess_type(name, path):
    """Employ voodoo magic to guess the type of *name* in *path*."""
    if name.rsplit('.', 1)[-1][0].isupper() and '#' not in path:
        return CLASS
    elif name.islower() and '#' not in path:
        return PACKAGE
    else:
        return METHOD
