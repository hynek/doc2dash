from __future__ import absolute_import, division, print_function

import pytest
import six

from characteristic import Attribute, attributes
from mock import patch
from zope.interface import implementer

from doc2dash.parsers.utils import (
    IParser,
    ParserEntry,
    TOCEntry,
    patch_anchors,
)


@implementer(IParser)
@attributes([
    Attribute("name", exclude_from_init=True, instance_of=six.text_type),
    Attribute("doc_path", instance_of=six.text_type),
    Attribute("_succeed_patching", default_value=True),
    Attribute("_patched_entries", default_factory=list)
])
class TestParser(object):
    name = "testparser"

    @staticmethod
    def detect(path):
        return True

    def parse(self):
        pass

    def find_and_patch_entry(self, soup, entry):
        if self._patched_entries is None:
            self._patched_entries = []
        self._patched_entries.append(entry)
        return self._succeed_patching


@pytest.fixture
def entries():
    """
    Test `ParserEntry`s
    """
    return [
        ParserEntry(name=u'foo', type=u'Method', path=u'bar.html#foo'),
        ParserEntry(name=u'qux', type=u'Class', path=u'bar.html'),
    ]


class TestPatchTOCAnchors(object):
    @pytest.mark.parametrize(
        "progressbar",
        [True, False]
    )
    def test_with_empty_db(self, progressbar):
        """
        Adding no entries does not cause an error.
        """
        parser = TestParser(doc_path=u"foo")
        toc = patch_anchors(parser, show_progressbar=progressbar)
        toc.close()

    def test_single_entry(self, monkeypatch, tmpdir, entries):
        """
        Only entries with URL anchors get patched.
        """
        foo = tmpdir.mkdir('foo')
        foo.join("bar.html").write("docs!")
        parser = TestParser(doc_path=six.text_type(foo))
        toc = patch_anchors(parser, show_progressbar=False)
        for e in entries:
            print(e)
            toc.send(e)
        toc.close()
        assert [
            TOCEntry(name=u'foo', type=u'Method', anchor=u'foo'),
        ] == parser._patched_entries

    def test_complains(self, entries, tmpdir):
        """
        If patching fails, a debug message is logged.
        """
        foo = tmpdir.mkdir('foo')
        foo.join("bar.html").write("docs!")
        parser = TestParser(doc_path=six.text_type(foo),
                            succeed_patching=False)
        toc = patch_anchors(parser, show_progressbar=False)
        for e in entries:
            toc.send(e)
        with patch('doc2dash.parsers.utils.log.debug') as mock:
            toc.close()
            assert mock.call_count == 1
