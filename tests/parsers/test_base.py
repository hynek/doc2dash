import os

from mock import patch

from doc2dash.parsers.base import _BaseParser, ParserEntry


class TestParser(_BaseParser):
    pass


def test_toc_with_empty_db():
    """
    Adding no entries does not cause an error.
    """
    p = TestParser('foo')
    toc = p.add_toc(show_progressbar=False)
    toc.close()

    p = TestParser('foo')
    toc = p.add_toc(show_progressbar=True)
    toc.close()


def test_add_toc_single_entry(monkeypatch, tmpdir):
    entries = [
        ParserEntry(name='foo', type='clm', path='bar.html#foo'),
        ParserEntry(name='qux', type='cl', path='bar.html'),
    ]
    monkeypatch.chdir(tmpdir)
    p = TestParser('foo')
    os.mkdir('foo')
    with open('foo/bar.html', 'w') as fp:
        fp.write('docs!')
    p.find_and_patch_entry = lambda x, y: True
    toc = p.add_toc(show_progressbar=False)
    for e in entries:
        toc.send(e)
    toc.close()

    p.find_and_patch_entry = lambda x, y: False
    toc = p.add_toc(show_progressbar=False)
    for e in entries:
        toc.send(e)
    with patch('doc2dash.parsers.base.log.debug') as mock:
        toc.close()
        assert mock.call_count == 1
