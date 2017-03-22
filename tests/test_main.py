from __future__ import absolute_import, division, print_function

import errno
import logging
import os
import plistlib
import shutil
import sqlite3
import sys

import attr
import pytest
import six

from click.testing import CliRunner
from mock import MagicMock, patch
from zope.interface import implementer

import doc2dash

from doc2dash import __main__ as main
from doc2dash.parsers.utils import ParserEntry, IParser


log = logging.getLogger(__name__)


@pytest.fixture
def runner():
    """
    Click's test helper.
    """
    return CliRunner()


class TestArguments(object):
    def test_fails_with_unknown_icon(self, runner, tmpdir, monkeypatch):
        """
        Fail if icon is not PNG.
        """
        p = tmpdir.mkdir("sub").join("bar.png")
        p.write("GIF89afoobarbaz")
        result = runner.invoke(main.main, [str(tmpdir), '-i', str(p)])

        assert result.output.endswith(" is not a valid PNG image.\n")
        assert 1 == result.exit_code

    def test_handles_unknown_doc_types(self, tmpdir, runner):
        """
        If docs are passed but are unknown, exit with EINVAL.
        """
        result = runner.invoke(main.main, [str(tmpdir.mkdir("foo"))])
        assert errno.EINVAL == result.exit_code

    def test_quiet_and_verbose_conflict(self, runner, tmpdir):
        """
        Ensure main() exits on -q + -v
        """
        result = runner.invoke(main.main,
                               [str(tmpdir.mkdir("foo")), '-q', '-v'])
        assert 1 == result.exit_code
        assert "makes no sense" in result.output


def test_normal_flow(monkeypatch, tmpdir, runner):
    """
    Integration test with a mock parser.
    """
    def fake_prepare(source, dest, name, index_page, enable_js,
                     online_redirect_url):
        os.mkdir(dest)
        db_conn = sqlite3.connect(":memory:")
        db_conn.row_factory = sqlite3.Row
        db_conn.execute(
            "CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, "
            "type TEXT, path TEXT)"
        )
        return main.DocSet(path=str(tmpdir), docs=u"data", plist=None,
                           db_conn=db_conn)

    monkeypatch.chdir(tmpdir)
    png_file = tmpdir.join("icon.png")
    png_file.write(main.PNG_HEADER, mode="wb")
    os.mkdir("foo")
    monkeypatch.setattr(main, "prepare_docset", fake_prepare)

    @implementer(IParser)
    @attr.s
    class FakeParser(object):
        doc_path = attr.ib(
            validator=attr.validators.instance_of(six.text_type))

        name = u"testtype"

        @staticmethod
        def detect(path):
            return True

        def parse(self):
            yield ParserEntry(name=u"testmethod", type=u"cm", path=u"testpath")

        def find_and_patch_entry(self, soup, entry):
            pass

    class fake_module:
        Parser = FakeParser

    expected = '''\
Converting testtype docs from "foo" to "./{name}.docset".
Parsing documentation...
Added 1 index entries.
Adding table of contents meta data...
Adding to Dash.app...
'''

    # alternative 1: use --parser
    sys.modules['fake_module'] = fake_module
    with patch("os.system") as system:
        result = runner.invoke(
            main.main, ["foo", "--parser", "fake_module.Parser", "-n", "bah",
                        "-a", "-i", str(png_file)]
        )
    assert expected.format(name='bah') == result.output
    assert 0 == result.exit_code
    assert ('open -a dash "./bah.docset"', ) == system.call_args[0]

    # alternative 2: patch doc2dash.parsers
    monkeypatch.setattr(doc2dash.parsers, "get_doctype", lambda _: FakeParser)
    with patch("os.system") as system:
        result = runner.invoke(
            main.main, ["foo", "-n", "bar", "-a", "-i", str(png_file)]
        )
    assert expected.format(name='bar') == result.output
    assert 0 == result.exit_code
    assert ('open -a dash "./bar.docset"', ) == system.call_args[0]

    # Again, just without adding and icon.
    with patch("os.system") as system:
        result = runner.invoke(
            main.main, ["foo", "-n", "baz"]
        )

    assert 0 == result.exit_code

    # some tests for --parser validation

    result = runner.invoke(main.main,
                           ['foo', '-n', 'bing', '--parser', 'no_dot'])
    assert "'no_dot' is not an import path" in result.output
    assert 2 == result.exit_code

    with patch("os.system") as system:
        result = runner.invoke(main.main, ['foo', '-n', 'bing', '--parser',
                                           'nonexistent_module.Parser'])
    assert "Could not import module 'nonexistent_module'" in result.output
    assert 2 == result.exit_code

    with patch("os.system") as system:
        result = runner.invoke(main.main, ['foo', '-n', 'bing', '--parser',
                                           'sys.NonexistentParser'])
    assert ("Failed to get attribute 'NonexistentParser' from module 'sys'"
            in result.output)
    assert 2 == result.exit_code


class TestSetupPaths(object):
    def test_works(self, tmpdir):
        """
        Integration tests with fake paths.
        """
        foo_path = str(tmpdir.join('foo'))
        os.mkdir(foo_path)
        assert (
            foo_path, str(tmpdir.join('foo.docset')), "foo"
        ) == main.setup_paths(
            foo_path, str(tmpdir), name=None, add_to_global=False,
            force=False
        )
        abs_foo = os.path.abspath(foo_path)
        assert (
            abs_foo, str(tmpdir.join('foo.docset')), "foo"
        ) == main.setup_paths(
            abs_foo, str(tmpdir), name=None, add_to_global=False,
            force=False
        )
        assert (
            abs_foo, str(tmpdir.join('baz.docset')), "baz"
        ) == main.setup_paths(
            abs_foo, str(tmpdir), name="baz", add_to_global=False,
            force=False
        )

    def test_add_to_global_overrides_destination(self):
        """
        Passing -A computes the destination and overrides an argument.
        """
        assert "~" not in main.DEFAULT_DOCSET_PATH  # resolved?
        assert (
            "foo", os.path.join(main.DEFAULT_DOCSET_PATH, "foo.docset"), "foo"
        ) == main.setup_paths(
            source="foo", name=None, destination="foobar",
            add_to_global=True, force=False
        )

    def test_detects_existing_dest(self, tmpdir, monkeypatch):
        """
        Exit with EEXIST if the selected destination already exists.
        """
        monkeypatch.chdir(tmpdir)
        os.mkdir('foo')
        os.mkdir('foo.docset')
        with pytest.raises(SystemExit) as e:
            main.setup_paths(
                source='foo', force=False, name=None, destination=None,
                add_to_global=False
            )
        assert e.value.code == errno.EEXIST

        main.setup_paths(
            source='foo', force=True, name=None, destination=None,
            add_to_global=False
        )
        assert not os.path.lexists('foo.docset')

    def test_deducts_name_with_trailing_slash(self, tmpdir, monkeypatch):
        """
        If the source path ends with a /, the name is still correctly deducted.
        """
        monkeypatch.chdir(tmpdir)
        os.mkdir('foo')
        assert "foo" == main.setup_paths(
            source='foo/', force=False, name=None,
            destination=None, add_to_global=False)[0]

    def test_cleans_name(self, tmpdir):
        """
        If the name ends with .docset, remove it.
        """
        d = tmpdir.mkdir("foo")
        assert "baz" == main.setup_paths(
            source=str(d), force=False, name="baz.docset", destination="bar",
            add_to_global=False,
        )[2]


class TestPrepareDocset(object):
    def test_plist_creation(self, monkeypatch, tmpdir):
        """
        All arguments should be reflected in the plist.
        """
        monkeypatch.chdir(tmpdir)
        m_ct = MagicMock()
        monkeypatch.setattr(shutil, 'copytree', m_ct)
        os.mkdir('bar')
        docset = main.prepare_docset(
            "some/path/foo", 'bar', name="foo", index_page=None,
            enable_js=False, online_redirect_url=None
        )
        m_ct.assert_called_once_with(
            'some/path/foo',
            'bar/Contents/Resources/Documents',
        )
        assert os.path.isfile('bar/Contents/Resources/docSet.dsidx')
        p = plistlib.readPlist(docset.plist)
        assert p == {
            'CFBundleIdentifier': 'foo',
            'CFBundleName': 'foo',
            'DocSetPlatformFamily': 'foo',
            'DashDocSetFamily': 'python',
            'isDashDocset': True,
            'isJavaScriptEnabled': False,
        }
        with sqlite3.connect('bar/Contents/Resources/docSet.dsidx') as db_conn:
            cur = db_conn.cursor()
            # ensure table exists and is empty
            cur.execute('select count(1) from searchIndex')
            assert cur.fetchone()[0] == 0

    def test_with_index_page(self, monkeypatch, tmpdir):
        """
        If an index page is passed, it is added to the plist.
        """
        monkeypatch.chdir(tmpdir)
        m_ct = MagicMock()
        monkeypatch.setattr(shutil, 'copytree', m_ct)
        os.mkdir('bar')
        docset = main.prepare_docset('some/path/foo', 'bar', name='foo',
                                     index_page='foo.html',
                                     enable_js=False,
                                     online_redirect_url=None)
        p = plistlib.readPlist(docset.plist)
        assert p == {
            'CFBundleIdentifier': 'foo',
            'CFBundleName': 'foo',
            'DocSetPlatformFamily': 'foo',
            'DashDocSetFamily': 'python',
            'isDashDocset': True,
            'dashIndexFilePath': 'foo.html',
            'isJavaScriptEnabled': False,
        }

    def test_with_javascript_enabled(self, monkeypatch, tmpdir):
        """
        If an index page is passed, it is added to the plist.
        """
        monkeypatch.chdir(tmpdir)
        m_ct = MagicMock()
        monkeypatch.setattr(shutil, 'copytree', m_ct)
        os.mkdir('bar')
        docset = main.prepare_docset('some/path/foo', 'bar', name='foo',
                                     index_page='foo.html',
                                     enable_js=True,
                                     online_redirect_url=None)
        p = plistlib.readPlist(docset.plist)
        assert p == {
            'CFBundleIdentifier': 'foo',
            'CFBundleName': 'foo',
            'DocSetPlatformFamily': 'foo',
            'DashDocSetFamily': 'python',
            'isDashDocset': True,
            'dashIndexFilePath': 'foo.html',
            'isJavaScriptEnabled': True,
        }

    def test_with_online_redirect_url(self, monkeypatch, tmpdir):
        """
        If an index page is passed, it is added to the plist.
        """
        monkeypatch.chdir(tmpdir)
        m_ct = MagicMock()
        monkeypatch.setattr(shutil, 'copytree', m_ct)
        os.mkdir('bar')
        docset = main.prepare_docset('some/path/foo', 'bar', name='foo',
                                     index_page='foo.html',
                                     enable_js=False,
                                     online_redirect_url="https://domain.com")
        p = plistlib.readPlist(docset.plist)
        assert p == {
            'CFBundleIdentifier': 'foo',
            'CFBundleName': 'foo',
            'DocSetPlatformFamily': 'foo',
            'DashDocSetFamily': 'python',
            'isDashDocset': True,
            'dashIndexFilePath': 'foo.html',
            'isJavaScriptEnabled': False,
            'DashDocSetFallbackURL': "https://domain.com",
        }


class TestSetupLogging(object):
    @pytest.mark.parametrize(
        "verbose, quiet, expected", [
            (False, False, logging.INFO),
            (True, False, logging.DEBUG),
            (False, True, logging.ERROR),
        ]
    )
    def test_logging(self, verbose, quiet, expected):
        """
        Ensure verbosity options cause the correct log level.
        """
        level = main.create_log_config(
            verbose, quiet
        )["loggers"]["doc2dash"]["level"]
        assert level is expected

    def test_quiet_and_verbose(self):
        """
        Fail if both -q and -v are passed.
        """
        with pytest.raises(ValueError) as e:
            main.create_log_config(verbose=True, quiet=True)
        assert "makes no sense" in e.value.args[0]
