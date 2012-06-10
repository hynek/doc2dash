import errno
import os
import sys
import tempfile

import mock
import pytest

from doc2dash import main


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


###########################################################################
#                            setup_paths tests                            #
###########################################################################


def test_setup_paths_works(monkeypatch):
    with tempfile.TemporaryDirectory() as td:
        monkeypatch.chdir(td)
        os.mkdir('foo')
        args = mock.MagicMock(source='foo')
        assert ('foo', 'foo.docset') == main.setup_paths(args)
        args.source = os.path.abspath('foo')
        assert (os.path.abspath('foo'), 'foo.docset') == main.setup_paths(args)


def test_setup_paths_detects_missing_source():
    args = mock.MagicMock(source='doesnotexist')
    with pytest.raises(SystemExit) as e:
        main.setup_paths(args)
    assert e.value.code == errno.ENOENT


def test_setup_paths_detects_source_is_file():
    args = mock.MagicMock(source='setup.py')
    with pytest.raises(SystemExit) as e:
        main.setup_paths(args)
    assert e.value.code == errno.ENOTDIR


def test_setup_paths_detects_existing_dest(monkeypatch):
    with tempfile.TemporaryDirectory() as td:
        monkeypatch.chdir(td)
        os.mkdir('foo')
        os.mkdir('foo.docset')
        args = mock.MagicMock(source='foo', force=False)
        with pytest.raises(SystemExit) as e:
            main.setup_paths(args)
        assert e.value.code == errno.EEXIST

        args.force = True
        main.setup_paths(args)
        assert not os.path.lexists('foo.docset')
