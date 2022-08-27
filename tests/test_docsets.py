import os
import shutil
import sqlite3

from unittest.mock import MagicMock

from doc2dash import docsets


class TestPrepareDocset:
    def test_plist_creation(self, monkeypatch, tmpdir):
        """
        All arguments should be reflected in the plist.
        """
        monkeypatch.chdir(tmpdir)
        m_ct = MagicMock()
        monkeypatch.setattr(shutil, "copytree", m_ct)
        os.mkdir("bar")
        docset = docsets.prepare_docset(
            "some/path/foo",
            "bar",
            name="foo",
            index_page=None,
            enable_js=False,
            online_redirect_url=None,
        )
        m_ct.assert_called_once_with(
            "some/path/foo", "bar/Contents/Resources/Documents"
        )

        assert os.path.isfile("bar/Contents/Resources/docSet.dsidx")

        p = docsets.read_plist(docset.plist)

        assert p == {
            "CFBundleIdentifier": "foo",
            "CFBundleName": "foo",
            "DocSetPlatformFamily": "foo",
            "DashDocSetFamily": "python",
            "DashDocSetDeclaredInStyle": "originalName",
            "isDashDocset": True,
            "isJavaScriptEnabled": False,
        }

        with sqlite3.connect("bar/Contents/Resources/docSet.dsidx") as db_conn:
            cur = db_conn.cursor()
            # ensure table exists and is empty
            cur.execute("select count(1) from searchIndex")

            assert cur.fetchone()[0] == 0

    def test_with_index_page(self, monkeypatch, tmpdir):
        """
        If an index page is passed, it is added to the plist.
        """
        monkeypatch.chdir(tmpdir)
        m_ct = MagicMock()
        monkeypatch.setattr(shutil, "copytree", m_ct)
        os.mkdir("bar")
        docset = docsets.prepare_docset(
            "some/path/foo",
            "bar",
            name="foo",
            index_page="foo.html",
            enable_js=False,
            online_redirect_url=None,
        )

        p = docsets.read_plist(docset.plist)

        assert p == {
            "CFBundleIdentifier": "foo",
            "CFBundleName": "foo",
            "DocSetPlatformFamily": "foo",
            "DashDocSetFamily": "python",
            "DashDocSetDeclaredInStyle": "originalName",
            "isDashDocset": True,
            "dashIndexFilePath": "foo.html",
            "isJavaScriptEnabled": False,
        }

    def test_with_javascript_enabled(self, monkeypatch, tmpdir):
        """
        If an index page is passed, it is added to the plist.
        """
        monkeypatch.chdir(tmpdir)
        m_ct = MagicMock()
        monkeypatch.setattr(shutil, "copytree", m_ct)
        os.mkdir("bar")
        docset = docsets.prepare_docset(
            "some/path/foo",
            "bar",
            name="foo",
            index_page="foo.html",
            enable_js=True,
            online_redirect_url=None,
        )

        p = docsets.read_plist(docset.plist)

        assert p == {
            "CFBundleIdentifier": "foo",
            "CFBundleName": "foo",
            "DocSetPlatformFamily": "foo",
            "DashDocSetFamily": "python",
            "DashDocSetDeclaredInStyle": "originalName",
            "isDashDocset": True,
            "dashIndexFilePath": "foo.html",
            "isJavaScriptEnabled": True,
        }

    def test_with_online_redirect_url(self, monkeypatch, tmpdir):
        """
        If an index page is passed, it is added to the plist.
        """
        monkeypatch.chdir(tmpdir)
        m_ct = MagicMock()
        monkeypatch.setattr(shutil, "copytree", m_ct)
        os.mkdir("bar")
        docset = docsets.prepare_docset(
            "some/path/foo",
            "bar",
            name="foo",
            index_page="foo.html",
            enable_js=False,
            online_redirect_url="https://domain.com",
        )

        p = docsets.read_plist(docset.plist)

        assert p == {
            "CFBundleIdentifier": "foo",
            "CFBundleName": "foo",
            "DocSetPlatformFamily": "foo",
            "DashDocSetFamily": "python",
            "DashDocSetDeclaredInStyle": "originalName",
            "isDashDocset": True,
            "dashIndexFilePath": "foo.html",
            "isJavaScriptEnabled": False,
            "DashDocSetFallbackURL": "https://domain.com",
        }
