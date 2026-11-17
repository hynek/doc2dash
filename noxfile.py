# SPDX-FileCopyrightText: 2012 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import re
import shutil
import tomllib

from pathlib import Path

import nox


DEFAULT_PYTHON = Path(".python-version-default").read_text().strip()

nox.options.sessions = ["pre_commit", "tests", "docs", "mypy"]
nox.options.reuse_existing_virtualenvs = True
nox.options.error_on_external_run = True

# First version with parallel support.
nox.needs_version = ">=2026.08.10"
nox.options.default_venv_backend = "uv|virtualenv"


MATCH_PYTHON = re.compile(r"\s+python\: \"(\d\.\d\d)\"").match
# Avoid dependency on a YAML lib using a questionable hack.
for line in Path(".readthedocs.yaml").read_text().splitlines():
    if m := MATCH_PYTHON(line):
        DOCS_PYTHON = m.group(1)
        break

pyp = tomllib.loads(Path("pyproject.toml").read_text())
ALL_SUPPORTED = [
    pv.rsplit(" ")[-1]
    for pv in pyp["project"]["classifiers"]
    if pv.startswith("Programming Language :: Python :: ")
]


@nox.session(allow_parallel=True)
def pre_commit(session: nox.Session) -> None:
    session.install("prek")

    session.run("prek", "run", "--all-files")


@nox.session(python=["pypy3.11", *ALL_SUPPORTED], allow_parallel=True)
def tests(session: nox.Session) -> None:
    session.install(".", "--group", "tests")

    # Ensure that rich doesn't add format sequences.
    env = {"TERM": "dumb"}

    session.run("coverage", "run", "-m", "pytest", *session.posargs, env=env)
    session.run("coverage", "run", "-m", "doc2dash", "--version")


@nox.session(requires=["tests"])
def coverage_report(session: nox.Session) -> None:
    session.install("coverage[toml]")

    session.run("coverage", "combine")
    session.run("coverage", "report")


@nox.session(python=DEFAULT_PYTHON, allow_parallel=True)
def mypy(session: nox.Session) -> None:
    session.install(".", "--group", "typing", "nox")

    session.run("mypy", "src", "noxfile.py")


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
    (html / ".buildinfo").unlink()
    (html / "searchindex.js").unlink()


@nox.session(python=DOCS_PYTHON, allow_parallel=True)
def docs(session: nox.Session) -> None:
    # Needs to be separate when using hashes.
    session.install("-r", "requirements/docs.txt")
    session.install("-e", ".")

    if session.posargs:
        session.run("zensical", *session.posargs)
    else:
        session.run("zensical", "build", "--clean", "--strict")


@nox.session(python=DOCS_PYTHON)
def pin_docs(session: nox.Session) -> None:
    session.install("uv")

    session.run(
        "uv", "pip", "compile",
        "--upgrade",
        "--group", "docs",
        "--index-url", "https://pypi.org/simple",
        "--generate-hashes",
        "--output-file", "requirements/docs.txt",
        "pyproject.toml",
    )  # fmt: skip
