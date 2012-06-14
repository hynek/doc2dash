import errno
import os
import re

from bs4 import BeautifulSoup

from doc2dash.parsers import types


POSSIBLE_INDEXES = [
        'genindex-all.html',
        'genindex.html',
]


def parse(docpath):
    """Parse sphinx docs at *path*.

    yield tuples of symbol name, type and path

    """
    for idx in POSSIBLE_INDEXES:
        try:
            soup = BeautifulSoup(open(os.path.join(docpath, idx)), 'lxml')
            break
        except IOError:
            pass
    else:
        raise IOError(errno.ENOENT, 'Essential index file not found.')

    for t in _parse_soup(soup):
        yield t


def _parse_soup(soup):
    for table in soup('table', {'class': 'genindextable'}):
        for td in table('td'):
            for dl in td('dl', recursive=False):
                for dt in dl('dt', recursive=False):
                    if not dt.a:
                        continue
                    type_, name = _get_type_and_name(dt.a.string)
                    if name:
                        yield name, type_, dt.a['href']
                    else:
                        name = _strip_annotation(dt.a.string)
                    dd = dt.next_sibling.next_sibling
                    if dd and dd.name == 'dd':
                        for y in _process_dd(name, dd):
                            yield y


RE_ANNO = re.compile(r'(\S+) \(.*\)')


def _strip_annotation(text):
    """ Transforms 'foo (class in bar)' to 'foo'.  """
    m = RE_ANNO.match(text)
    if m:
        return m.group(1)
    else:
        return text.strip()


def _process_dd(name, dd):
    """Process a <dd> block as used by Sphinx on multiple symbols/name.

    All symbols inherit the *name* of the first.

    """
    for dt in dd('dt'):
        text = dt.text.strip()
        type_ = _get_type(text)
        if type_:
            if type_ == _IN_MODULE:
                type_ = _guess_type_by_name(name)
            yield name, type_, dt.a['href']


def _guess_type_by_name(name):
    """Module level functions and constants are not distinguishable."""
    if name.endswith('()'):
        return types.FUNCTION
    else:
        return types.CONSTANT


def _get_type(text):
    return _get_type_and_name(text)[0]


_IN_MODULE = '_in_module'
TYPE_MAPPING = [
        (re.compile(r'(.*)\(\S+ method\)$'), types.METHOD),
        (re.compile(r'(.*)\(.*function\)$'), types.FUNCTION),
        (re.compile(r'(.*)\(\S+ attribute\)$'), types.ATTRIBUTE),
        (re.compile(r'(.*)\(\S+ member\)$'), types.ATTRIBUTE),
        (re.compile(r'(.*)\(class in \S+\)$'), types.CLASS),
        (re.compile(r'(.*)\(built-in class\)$'), types.CLASS),
        (re.compile(r'(.*)\(built-in variable\)$'), types.CONSTANT),
        (re.compile(r'(.*)\(module\)$'), types.PACKAGE),
        (re.compile(r'(.*)\(in module \S+\)$'), _IN_MODULE),
]


def _get_type_and_name(text):
    for mapping in TYPE_MAPPING:
        match = mapping[0].match(text)
        if match:
            name = match.group(1).strip()
            type_ = mapping[1]
            if type_ == _IN_MODULE and name:
                type_ = _guess_type_by_name(name)
            return type_, name
    else:
        return None, None
