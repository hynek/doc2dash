# SPDX-License-Identifier: MIT

"""
Query the Read The Docs API and transform all active versions into
a mkdocs-material-theme-compatible versions.json file.

Needs to run after each tag.
"""

import json
import os
import sys

from typing import Any, TypedDict

import urllib3


def main(project: str, token: str) -> None:
    client = urllib3.PoolManager(
        headers={"Authorization": "Token " + token},
    )

    versions = collect_versions(client, project)
    with open("docs/versions.json", "w") as f:
        json.dump(versions, f, indent=2)
        f.write("\n")

    client.clear()  # type: ignore[no-untyped-call]


class Version(TypedDict):
    title: str
    aliases: list[str]
    version: str


def sieve_versions(vers: list[dict[str, Any]]) -> list[Version]:
    rv: list[Version] = []
    latest: Version | None = None
    for v in vers:
        vn = v["verbose_name"]
        if vn == "stable" or not v["active"]:
            continue

        path = v["slug"]
        if vn == "latest":
            latest = {
                "title": "Unreleased",
                "aliases": ["main", "latest"],
                "version": path,
            }
            continue

        rv.append({"title": vn, "version": path, "aliases": []})

    if latest:
        rv.insert(1, latest)

    return rv


def collect_versions(
    client: urllib3.PoolManager, project: str
) -> list[Version]:
    versions: list[Version] = []

    p = json.loads(
        client.request(  # type: ignore[no-untyped-call]
            "GET",
            f"https://readthedocs.org/api/v3/projects/{project}/versions/",
        ).data
    )
    versions.extend(sieve_versions(p["results"]))

    while n := p["next"]:
        p = json.loads(
            client.request("GET", n).data  # type: ignore[no-untyped-call]
        )
        versions.extend(sieve_versions(p["results"]))

    versions[0]["aliases"].append("Latest Stable Release")

    return versions


if __name__ == "__main__":
    project = sys.argv[1]
    token = os.environ["RTD_TOKEN"]

    main(project, token)
