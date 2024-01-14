# SPDX-FileCopyrightText: 2012 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

import shutil
import sqlite3

from pathlib import Path
from unittest.mock import Mock

from doc2dash import docsets


class TestPrepareDocset:
    def test_plist_creation(self, monkeypatch, tmp_path):
        """
        All arguments should be reflected in the plist.
        """
        monkeypatch.chdir(tmp_path)
        m_ct = Mock()
        monkeypatch.setattr(shutil, "copytree", m_ct)
        (tmp_path / "bar").mkdir()

        docset = docsets.prepare_docset(
            Path("some/path/foo"),
            Path("bar"),
            name="foo",
            index_page=None,
            enable_js=False,
            online_redirect_url=None,
            playground_url=None,
            icon=None,
            icon_2x=None,
            full_text_search=docsets.FullTextSearch.OFF,
        )

        m_ct.assert_called_once_with(
            Path("some/path/foo"), Path("bar/Contents/Resources/Documents")
        )
        assert Path("bar/Contents/Resources/docSet.dsidx").is_file()

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

    def test_with_index_page(self, monkeypatch, tmp_path):
        """
        If an index page is passed, it is added to the plist.
        """
        monkeypatch.chdir(tmp_path)
        m_ct = Mock()
        monkeypatch.setattr(shutil, "copytree", m_ct)
        (tmp_path / "bar").mkdir()

        docset = docsets.prepare_docset(
            Path("some/path/foo"),
            Path("bar"),
            name="foo",
            index_page="foo.html",
            enable_js=False,
            online_redirect_url=None,
            playground_url=None,
            icon=None,
            icon_2x=None,
            full_text_search=docsets.FullTextSearch.OFF,
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

    def test_with_javascript_enabled(self, monkeypatch, tmp_path):
        """
        If an index page is passed, it is added to the plist.
        """
        monkeypatch.chdir(tmp_path)
        m_ct = Mock()
        monkeypatch.setattr(shutil, "copytree", m_ct)
        (tmp_path / "bar").mkdir()

        docset = docsets.prepare_docset(
            Path("some/path/foo"),
            Path("bar"),
            name="foo",
            index_page="foo.html",
            enable_js=True,
            online_redirect_url=None,
            playground_url=None,
            icon=None,
            icon_2x=None,
            full_text_search=docsets.FullTextSearch.OFF,
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

    def test_with_online_redirect_url(self, monkeypatch, tmp_path):
        """
        If an index page is passed, it is added to the plist.
        """
        monkeypatch.chdir(tmp_path)
        m_ct = Mock()
        monkeypatch.setattr(shutil, "copytree", m_ct)
        (tmp_path / "bar").mkdir()

        docset = docsets.prepare_docset(
            Path("some/path/foo"),
            Path("bar"),
            name="foo",
            index_page="foo.html",
            enable_js=False,
            online_redirect_url="https://domain.com",
            playground_url=None,
            icon=None,
            icon_2x=None,
            full_text_search=docsets.FullTextSearch.OFF,
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

    def test_with_playground_url(self, monkeypatch, tmp_path):
        """
        If a playground URL is passed, it is added to the plist.
        """
        monkeypatch.chdir(tmp_path)
        m_ct = Mock()
        monkeypatch.setattr(shutil, "copytree", m_ct)
        (tmp_path / "bar").mkdir()

        docset = docsets.prepare_docset(
            Path("some/path/foo"),
            Path("bar"),
            name="foo",
            index_page="foo.html",
            enable_js=False,
            online_redirect_url=None,
            playground_url="https://repl.it/F9J7/1",
            icon=None,
            icon_2x=None,
            full_text_search=docsets.FullTextSearch.OFF,
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
            "DashDocSetPlayURL": "https://repl.it/F9J7/1",
        }

    def test_full_text_search_on(self, tmp_path, sphinx_built):
        """
        If full text search is enabled, it's added to the plist.
        """
        icon = Path("tests") / "logo.png"
        dest = tmp_path / "bar"

        docset = docsets.prepare_docset(
            sphinx_built,
            dest,
            name="foo",
            index_page=None,
            enable_js=False,
            online_redirect_url=None,
            playground_url=None,
            icon=None,
            icon_2x=icon,
            full_text_search=docsets.FullTextSearch.ON,
        )

        p = docsets.read_plist(docset.plist)

        assert p["DashDocSetDefaultFTSEnabled"] is True
        assert "DashDocSetFTSNotSupported" not in p

    def test_full_text_search_forbidden(self, tmp_path, sphinx_built):
        """
        If full text search is forbidden, it's added to the plist.
        """
        icon = Path("tests") / "logo.png"
        dest = tmp_path / "bar"

        docset = docsets.prepare_docset(
            sphinx_built,
            dest,
            name="foo",
            index_page=None,
            enable_js=False,
            online_redirect_url=None,
            playground_url=None,
            icon=None,
            icon_2x=icon,
            full_text_search=docsets.FullTextSearch.FORBIDDEN,
        )

        p = docsets.read_plist(docset.plist)

        assert p["DashDocSetFTSNotSupported"] is True
        assert "DashDocSetDefaultFTSEnabled" not in p

    def test_with_icon(self, tmp_path, sphinx_built):
        """
        If an icon is passed, it's copied to the root of the docset.
        """
        icon = Path("tests") / "logo.png"
        dest = tmp_path / "bar"

        docsets.prepare_docset(
            sphinx_built,
            dest,
            name="foo",
            index_page=None,
            enable_js=False,
            online_redirect_url=None,
            playground_url=None,
            icon=icon,
            icon_2x=None,
            full_text_search=docsets.FullTextSearch.OFF,
        )

        assert (Path(dest) / "icon.png").exists()

    def test_with_icon_2x(self, tmp_path, sphinx_built):
        """
        If an icon is passed, it's copied to the root of the docset.
        """
        icon = Path("tests") / "logo.png"
        dest = tmp_path / "bar"

        docsets.prepare_docset(
            sphinx_built,
            dest,
            name="foo",
            index_page=None,
            enable_js=False,
            online_redirect_url=None,
            playground_url=None,
            icon=None,
            icon_2x=icon,
            full_text_search=docsets.FullTextSearch.OFF,
        )

        assert (Path(dest) / "icon@2x.png").exists()
