import errno
import os
import plistlib
import shutil
import sqlite3
import sys
import tempfile

import pytest
from mock import MagicMock

import doc2dash
from doc2dash import main
from doc2dash.parsers.doctype import DocType


args = MagicMock(name='args')


def test_fails_without_source(capsys, monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['doc2dash'])
    with pytest.raises(SystemExit):
        main.main()

    out, err = capsys.readouterr()
    assert out == ''
    assert 'doc2dash: error: too few arguments' in err


def test_handles_unknown_doc_types(monkeypatch):
    with tempfile.TemporaryDirectory() as td:
        monkeypatch.chdir(td)
        monkeypatch.setattr(sys, 'argv', ['doc2dash', 'foo'])
        os.mkdir('foo')
        with pytest.raises(SystemExit) as e:
            main.main()
        assert e.value.code == errno.EINVAL


def test_normal_flow(monkeypatch, capsys):

    def _fake_prepare(args, dest):
        db_conn = sqlite3.connect(':memory:')
        db_conn.execute(
                'CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, '
                'type TEXT, path TEXT)'
        )
        return 'data', db_conn

    def _yielder(path):
        yield 'testmethod', 'testpath', 'cm'

    with tempfile.TemporaryDirectory() as td:
        monkeypatch.chdir(td)
        os.mkdir('foo')
        monkeypatch.setattr(sys, 'argv', ['doc2dash', 'foo', '-n', 'bar'])
        monkeypatch.setattr(main, 'prepare_docset', _fake_prepare)
        dt = DocType('testtype', lambda _: True, _yielder)
        monkeypatch.setattr(doc2dash.parsers, 'get_doctype', lambda _: dt)
        main.main()

    out, err = capsys.readouterr()
    assert err == ''
    assert out == '''\
Converting testtype docs from "foo" to "bar.docset".
Parsing HTML...
Added 1 index entries.
'''


###########################################################################
#                            setup_paths tests                            #
###########################################################################


def test_setup_paths_works(monkeypatch):
    with tempfile.TemporaryDirectory() as td:
        monkeypatch.chdir(td)
        os.mkdir('foo')
        args.configure_mock(source='foo', name=None)
        assert ('foo', 'foo.docset') == main.setup_paths(args)
        args.source = os.path.abspath('foo')
        assert (os.path.abspath('foo'), 'foo.docset') == main.setup_paths(args)
        assert args.name == 'foo'
        args.name = 'baz.docset'
        assert (os.path.abspath('foo'), 'baz.docset') == main.setup_paths(args)
        assert args.name == 'baz'


def test_setup_paths_detects_missing_source():
    args.configure_mock(source='doesnotexist', name=None)
    with pytest.raises(SystemExit) as e:
        main.setup_paths(args)
    assert e.value.code == errno.ENOENT


def test_setup_paths_detects_source_is_file():
    args.configure_mock(source='setup.py', name=None)
    with pytest.raises(SystemExit) as e:
        main.setup_paths(args)
    assert e.value.code == errno.ENOTDIR


def test_setup_paths_detects_existing_dest(monkeypatch):
    with tempfile.TemporaryDirectory() as td:
        monkeypatch.chdir(td)
        os.mkdir('foo')
        os.mkdir('foo.docset')
        args.configure_mock(source='foo', force=False, name=None)
        with pytest.raises(SystemExit) as e:
            main.setup_paths(args)
        assert e.value.code == errno.EEXIST

        args.force = True
        main.setup_paths(args)
        assert not os.path.lexists('foo.docset')


def test_prepare_docset(monkeypatch):
    with tempfile.TemporaryDirectory() as td:
        monkeypatch.chdir(td)
        m_ct = MagicMock()
        monkeypatch.setattr(shutil, 'copytree', m_ct)
        os.mkdir('bar')
        args.configure_mock(source='some/path/foo', name='foo')
        main.prepare_docset(args, 'bar')
        m_ct.assert_called_once_with(
                'some/path/foo',
                'bar/Contents/Resources/Documents',
        )
        assert os.path.isfile('bar/Contents/Resources/docSet.dsidx')
        p = plistlib.readPlist('bar/Contents/Info.plist')
        assert p == {
                'CFBundleIdentifier': 'foo',
                'CFBundleName': 'foo',
                'DocSetPlatformFamily': 'python',
                'DashDocSetFamily': 'python',
                'isDashDocset': True,
        }
        with sqlite3.connect('bar/Contents/Resources/docSet.dsidx') as db_conn:
            cur = db_conn.cursor()
            # ensure table exists and is empty
            cur.execute('select count(1) from searchIndex')
            assert cur.fetchone()[0] == 0
