from __future__ import absolute_import, division, print_function

import codecs
import errno
import logging
import os
import re

import six

from bs4 import BeautifulSoup
from characteristic import attributes
from zope.interface import implementer

from . import types
from .utils import IParser, ParserEntry, has_file_with
from .intersphinx import find_and_patch_entry


log = logging.getLogger(__name__)


@implementer(IParser)
@attributes(["doc_path"])
class SphinxParser(object):
    """
    Fallback HTML-based parser for Sphinx.
    """
    name = 'sphinx'

    @staticmethod
    def detect(path):
        return has_file_with(
            path,  "_static/searchtools.js", b'* Sphinx JavaScript util'
        )

    def parse(self):
        """
        Parse sphinx HTML docs at self.doc_path*.

        yield `ParserEntry`s
        """
        for idx in POSSIBLE_INDEXES:
            try:
                soup = BeautifulSoup(
                    codecs.open(os.path.join(self.doc_path, idx),
                                mode="r", encoding="utf-8"),
                    'lxml'
                )
                break
            except IOError:
                pass
        else:
            raise IOError(errno.ENOENT, 'Essential index file not found.')

        for t in _parse_soup(soup):
            yield t

    def find_and_patch_entry(self, soup, entry):  # pragma: nocover
        return find_and_patch_entry(soup, entry)


POSSIBLE_INDEXES = [
    'genindex-all.html',
    'genindex.html',
]


def _parse_soup(soup):
    for table in soup('table', {'class': 'genindextable'}):
        for td in table('td'):
            for dl in td('dl', recursive=False):
                for dt in dl('dt', recursive=False):
                    if not dt.a:
                        continue
                    type_, name = _get_type_and_name(dt.a.string)
                    if name:
                        href = six.text_type(dt.a['href'])
                        tmp_name = _url_to_name(href, type_)
                        if not tmp_name.startswith(u'index-'):
                            yield ParserEntry(name=tmp_name,
                                              type=type_,
                                              path=href)
                    else:
                        name = _strip_annotation(dt.a.string)
                    dd = dt.next_sibling.next_sibling
                    if dd and dd.name == 'dd':
                        for y in _process_dd(name, dd):
                            yield y


RE_ANNO = re.compile(six.text_type(r'(.+) \(.*\)'))


def _strip_annotation(text):
    """
    Transforms 'foo (class in bar)' to 'foo'.
    """
    m = RE_ANNO.match(text)
    if m:
        return m.group(1)
    else:
        return text.strip()


def _url_to_name(url, type_):
    """
    Certain types have prefixes in names we have to strip before adding.
    """
    if type_ == types.PACKAGE or type_ == types.CONSTANT and u'opcode-' in url:
        return url.split(u'#')[1][7:]
    else:
        return url.split(u'#')[1]


def _process_dd(name, dd):
    """
    Process a <dd> block as used by Sphinx on multiple symbols/name.

    All symbols inherit the *name* of the first.
    """
    for dt in dd('dt'):
        text = dt.text.strip()
        type_ = _get_type(text)
        if type_:
            if type_ == _IN_MODULE:
                type_ = _guess_type_by_name(name)
            full_name = _url_to_name(six.text_type(dt.a[u'href']), type_)
            if not full_name.startswith(u'index-'):
                yield ParserEntry(name=full_name,
                                  type=type_,
                                  path=six.text_type(dt.a[u'href']))


def _guess_type_by_name(name):
    """
    Module level functions and constants are not distinguishable.
    """
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
    (re.compile(r'(.*)\(opcode\)$'), types.CONSTANT),
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
