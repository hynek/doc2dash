# SPDX-FileCopyrightText: 2012 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import os
import re
import shutil
import sys

from pathlib import Path

import nox


DEFAULT_PYTHON = Path(".python-version-default").read_text().strip()

nox.options.sessions = ["pre_commit", "tests", "docs", "mypy"]
nox.options.reuse_existing_virtualenvs = True
nox.options.error_on_external_run = True

MATCH_PYTHON = re.compile(r"\s+python\: \"(\d\.\d\d)\"").match
# Avoid dependency on a YAML lib using a questionable hack.
for line in Path(".readthedocs.yaml").read_text().splitlines():
    if m := MATCH_PYTHON(line):
        DOCS_PYTHON = m.group(1)
        break


@nox.session
def pre_commit(session: nox.Session) -> None:
    session.install("pre-commit")

    session.run("pre-commit", "run", "--all-files")


@nox.session(python=["pypy3.10", "3.8", "3.9", "3.10", "3.11", "3.12"])
def tests(session: nox.Session) -> None:
    session.install(".[tests]")

    # Ensure that rich doesn't add format sequences.
    env = {"TERM": "dumb"}

    session.run("coverage", "run", "-m", "pytest", *session.posargs, env=env)
    session.run("coverage", "run", "-m", "doc2dash", "--version")

    if os.environ.get("CI") != "true":
        session.notify("coverage_report")


@nox.session
def coverage_report(session: nox.Session) -> None:
    session.install("coverage[toml]")

    session.run("coverage", "combine")
    session.run("coverage", "report")


@nox.session(python=DEFAULT_PYTHON)
def mypy(session: nox.Session) -> None:
    session.install(".[typing]")

    session.run("mypy", "src", "docs/update-rtd-versions.py", "noxfile.py")


@nox.session
def rebuild_sample_docs(session: nox.Session) -> None:
    session.install(".", "sphinx")
    session.chdir(
        Path("tests") / "parsers" / "intersphinx" / "example-sphinx-docs"
    )

    # Awkward name to avoid "_build" / "build" from .gitignore.
    session.run("sphinx-build", "-M", "html", "source", "built_docs")

    # Clean up stuff we don't need.
    built = Path("built_docs")
    html = built / "html"

    shutil.rmtree(built / "doctrees")
    shutil.rmtree(html / "_sources")
    shutil.rmtree(html / "_static")
    os.remove(html / ".buildinfo")
    os.remove(html / "searchindex.js")


@nox.session(python=DOCS_PYTHON)
def docs(session: nox.Session) -> None:
    # Needs to be separate when using hashes.
    session.install("-r", "requirements/docs.txt")
    session.install("-e", ".")

    if session.posargs:
        session.run("mkdocs", *session.posargs)
    else:
        session.run("mkdocs", "build", "--clean", "--strict")


@nox.session(python=DOCS_PYTHON)
def pin_docs(session: nox.Session) -> None:
    session.install("pip-tools>=6.8.0")

    session.run(
        # fmt: off
        "pip-compile",
        "--upgrade",
        "--allow-unsafe",   # otherwise install fails due to setuptools
        "--extra", "docs",
        "--index-url", "https://pypi.org/simple",
        "--generate-hashes",
        "--output-file", "requirements/docs.txt",
        "pyproject.toml",
        # fmt: on
    )


@nox.session
def update_rtd_versions(session: nox.Session) -> None:
    session.install("urllib3")

    session.run("python", "docs/update-rtd-versions.py", "doc2dash")


@nox.session
def oxidize(session: nox.Session) -> None:
    """
    Build a doc2dash binary with PyOxidizer.
    """
    env = os.environ.copy()
    env["PIP_REQUIRE_VIRTUALENV"] = "0"

    # standalone_static doesn't work on macOS and gives us musl builds on
    # Linux. Since you get one binary on both, dynamic standalone ~should be
    # fine~.
    if sys.platform == "win32":
        flavor = "standalone_static"
    else:
        flavor = "standalone"

    session.install("pyoxidizer")

    session.run("pyoxidizer", "-V")
    session.run(
        # fmt: off
        "pyoxidizer",
        "build",
        "--release",
        "--var", "flavor", flavor,
        "--var", "platform", sys.platform,
        # fmt: on
        env=env,
    )


@nox.session
def pin_for_pyoxidizer(session: nox.Session) -> None:
    """
    Pin the Python dependencies that are used for vendoring by PyOxidizer.
    """
    session.install("pip-tools>=6.8.0")

    session.run(
        # fmt: off
        "pip-compile",
        "--upgrade",
        "--index-url", "https://pypi.org/simple",
        "--generate-hashes",
        "--resolver", "backtracking",
        "--output-file", f"requirements/pyoxidizer-{sys.platform}.txt",
        "pyproject.toml",
        # fmt: on
    )


@nox.session
def download_and_package_binaries(session: nox.Session) -> None:
    """
    Download latest binaries and package them up for release upload.
    """
    shutil.rmtree("binaries", ignore_errors=True)

    tag = session.run(
        "git", "describe", "--abbrev=0", "--tags", external=True, silent=True
    ).strip()

    print("Downloading for git tag", tag)

    run_id = session.run(
        # fmt: off
        "gh", "run", "list",
        "--workflow", "Build binaries using pyOxidizer",
        "--branch", tag,
        "--json", "databaseId",
        "--jq", ".[0].databaseId",
        # fmt: on
        external=True,
        silent=True,
    ).strip()

    session.run("gh", "run", "download", run_id, external=True)

    for arch_path in Path("binaries").glob("*"):
        arch = arch_path.name
        with session.chdir(arch_path / "release/install"):
            d = Path("doc2dash")
            if d.exists():  # i.e. not Windows
                d.chmod(0o755)
            session.run(
                "zip",
                f"../../../doc2dash.{arch}.zip",
                "COPYING.txt",
                "doc2dash",
                "doc2dash.exe",
                external=True,
            )
