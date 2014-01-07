import errno
import logging
import os
import plistlib
import shutil
import sqlite3
import sys
import tempfile

import pytest
from mock import MagicMock, patch

import doc2dash
from doc2dash import __main__ as main


log = logging.getLogger(__name__)
args = MagicMock(name='args', A=False)


def test_fails_without_source(capsys, monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['doc2dash'])
    with pytest.raises(SystemExit):
        main.main()

    out, err = capsys.readouterr()
    assert out == ''
    assert ('doc2dash: error: too few arguments' in err
            or 'error: the following arguments are required: source' in err)


def test_fails_with_unknown_icon(capsys, monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['doc2dash', 'foo', '-i', 'bar.bmp'])
    with pytest.raises(SystemExit):
        main.main()

    out, err = capsys.readouterr()
    assert err == ''
    assert 'Please supply a PNG icon.' in out


def test_fails_with_inxistent_index_page(capsys, monkeypatch):
    """
    Fail if an index is supplied but doesn't exit.
    """
    monkeypatch.setattr(sys, 'argv', ['doc2dash', 'foo', '-I', 'bar.html'])
    with pytest.raises(SystemExit):
        main.main()

    out, err = capsys.readouterr()
    assert err == ''
    assert 'Index file bar.html does not exists.' in out


def test_handles_unknown_doc_types(monkeypatch):
    with tempfile.TemporaryDirectory() as td:
        monkeypatch.chdir(td)
        monkeypatch.setattr(sys, 'argv', ['doc2dash', 'foo'])
        os.mkdir('foo')
        with pytest.raises(SystemExit) as e:
            main.main()
        assert e.value.code == errno.EINVAL


def test_normal_flow(monkeypatch):

    def _fake_prepare(args, dest):
        db_conn = sqlite3.connect(':memory:')
        db_conn.row_factory = sqlite3.Row
        db_conn.execute(
            'CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, '
            'type TEXT, path TEXT)'
        )
        return 'data', db_conn

    def _yielder():
        yield 'testmethod', 'testpath', 'cm'

    with tempfile.TemporaryDirectory() as td:
        monkeypatch.chdir(td)
        os.mkdir('foo')
        monkeypatch.setattr(sys, 'argv', ['doc2dash', 'foo', '-n', 'bar',
                                          '-a', '-i', 'qux.png'])
        monkeypatch.setattr(main, 'prepare_docset', _fake_prepare)
        dt = MagicMock(detect=lambda _: True)
        dt.name = 'testtype'
        dt.return_value = MagicMock(parse=_yielder)
        monkeypatch.setattr(doc2dash.parsers, 'get_doctype', lambda _: dt)
        with patch('doc2dash.__main__.log.info') as info, \
                patch('os.system') as system, \
                patch('shutil.copy2') as cp:
            main.main()
            # assert mock.call_args_list is None
            out = '\n'.join(call[0][0] for call in info.call_args_list) + '\n'
            assert system.call_args[0] == ('open -a dash "bar.docset"', )
            assert cp.call_args[0] == ('qux.png', 'bar.docset/icon.png')

    assert out == '''\
Converting testtype docs from "foo" to "bar.docset".
Parsing HTML...
Added 1 index entries.
Adding table of contents meta data...
Adding to dash...
'''


###########################################################################
#                            setup_paths tests                            #
###########################################################################


def test_setup_paths_works(monkeypatch):
    with tempfile.TemporaryDirectory() as td:
        foo_path = os.path.join(td, 'foo')
        os.mkdir(foo_path)
        args.configure_mock(source=foo_path, name=None, destination=td)
        assert ((foo_path, os.path.join(td, 'foo.docset')) ==
                main.setup_paths(args))
        abs_foo = os.path.abspath(foo_path)
        args.source = abs_foo
        assert ((abs_foo, os.path.join(td, 'foo.docset')) ==
                main.setup_paths(args))
        assert args.name == 'foo'
        args.name = 'baz.docset'
        assert ((abs_foo, os.path.join(td, 'baz.docset')) ==
                main.setup_paths(args))
        assert args.name == 'baz'


def test_A_overrides_destination(monkeypatch):
    assert '~' not in main.DEFAULT_DOCSET_PATH  # resolved?
    args.configure_mock(source='doc2dash', name=None, destination='foobar',
                        A=True)
    assert ('foo', os.path.join(main.DEFAULT_DOCSET_PATH, 'foo.docset') ==
            main.setup_paths(args))


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
        args.configure_mock(source='foo', force=False, name=None,
                            destination=None, A=False)
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
        args.configure_mock(
            source='some/path/foo', name='foo', index_page=None)
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
            'DocSetPlatformFamily': 'foo',
            'DashDocSetFamily': 'python',
            'isDashDocset': True,
        }
        with sqlite3.connect('bar/Contents/Resources/docSet.dsidx') as db_conn:
            cur = db_conn.cursor()
            # ensure table exists and is empty
            cur.execute('select count(1) from searchIndex')
            assert cur.fetchone()[0] == 0


def test_prepare_docset_index_page(monkeypatch, tmpdir):
    """
    If an index page is passed, it is added to the plist.
    """
    monkeypatch.chdir(tmpdir)
    m_ct = MagicMock()
    monkeypatch.setattr(shutil, 'copytree', m_ct)
    os.mkdir('bar')
    args.configure_mock(
        source='some/path/foo', name='foo', index_page='foo.html')
    main.prepare_docset(args, 'bar')
    p = plistlib.readPlist('bar/Contents/Info.plist')
    assert p == {
        'CFBundleIdentifier': 'foo',
        'CFBundleName': 'foo',
        'DocSetPlatformFamily': 'foo',
        'DashDocSetFamily': 'python',
        'isDashDocset': True,
        'dashIndexFilePath': 'foo.html',
    }


###########################################################################
#                           setup_logging tests                           #
###########################################################################


def _check_logging(verbose, quiet, expect):
    args.configure_mock(verbose=verbose, quiet=quiet)
    assert main.determine_log_level(args) is expect


def test_logging(monkeypatch):
    with pytest.raises(ValueError):
        _check_logging(True, True, logging.INFO)
    _check_logging(False, False, logging.INFO)
    _check_logging(True, False, logging.DEBUG)
    _check_logging(False, True, logging.ERROR)

    monkeypatch.setattr(sys, 'argv', ['doc2dash', 'foo', '-q', '-v'])
    with pytest.raises(SystemExit):
        main.main()
