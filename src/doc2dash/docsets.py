# SPDX-FileCopyrightText: 2012 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from enum import Enum

import os
import plistlib
import shutil
import sqlite3

from functools import cached_property
from pathlib import Path

import attrs


@attrs.frozen
class DocSet:
    """
    Summary of docset path and parameters.
    """

    path: Path
    plist: Path
    db_conn: sqlite3.Connection

    @cached_property
    def docs(self) -> Path:
        return self.path / "Contents" / "Resources" / "Documents"


class FullTextSearch(Enum):
    ON = "on"
    OFF = "off"
    FORBIDDEN = "forbidden"


def prepare_docset(
    source: Path,
    dest: Path,
    name: str,
    index_page: Path | None,
    enable_js: bool,
    online_redirect_url: str | None,
    playground_url: str | None,
    icon: Path | None,
    icon_2x: Path | None,
    full_text_search: FullTextSearch,
) -> DocSet:
    """
    Create boilerplate files & directories and copy vanilla docs inside.

    Return a tuple of path to resources and connection to sqlite db.
    """
    resources = dest / "Contents" / "Resources"
    docs = resources / "Documents"
    os.makedirs(resources)

    db_conn = sqlite3.connect(resources / "docSet.dsidx")
    db_conn.row_factory = sqlite3.Row
    db_conn.execute(
        "CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, "
        "type TEXT, path TEXT)"
    )
    db_conn.commit()

    plist_path = dest / "Contents" / "Info.plist"
    plist_cfg: dict[str, str | bool] = {
        "CFBundleIdentifier": name,
        "CFBundleName": name,
        "DocSetPlatformFamily": name.lower(),
        "DashDocSetFamily": "python",
        "DashDocSetDeclaredInStyle": "originalName",
        "isDashDocset": True,
        "isJavaScriptEnabled": enable_js,
    }
    if index_page is not None:
        plist_cfg["dashIndexFilePath"] = str(index_page)
    if online_redirect_url is not None:
        plist_cfg["DashDocSetFallbackURL"] = online_redirect_url
    if playground_url is not None:
        plist_cfg["DashDocSetPlayURL"] = playground_url
    if full_text_search is FullTextSearch.FORBIDDEN:
        plist_cfg["DashDocSetFTSNotSupported"] = True
    if full_text_search is FullTextSearch.ON:
        plist_cfg["DashDocSetDefaultFTSEnabled"] = True

    write_plist(plist_cfg, plist_path)

    shutil.copytree(source, docs)

    if icon:
        shutil.copy2(icon, dest / "icon.png")

    if icon_2x:
        shutil.copy2(icon_2x, dest / "icon@2x.png")

    return DocSet(path=dest, plist=plist_path, db_conn=db_conn)


def read_plist(full_path: Path) -> dict[str, str | bool]:
    with full_path.open("rb") as fp:
        return plistlib.load(fp)  # type: ignore[no-any-return]


def write_plist(plist: dict[str, str | bool], full_path: Path) -> None:
    with full_path.open("wb") as fp:
        plistlib.dump(plist, fp)
