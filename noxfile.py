from __future__ import annotations

import os
import shutil
import sys

from pathlib import Path

import nox


DEFAULT_PYTHON = "3.10"

nox.options.sessions = ["pre_commit", "tests_cov", "docs", "mypy"]
nox.options.reuse_existing_virtualenvs = True
nox.options.error_on_external_run = True


@nox.session
def pre_commit(session: nox.Session) -> None:
    session.install("pre-commit")

    session.run("pre-commit", "run", "--all-files", "--show-diff-on-failure")


@nox.session(python=["3.8", "3.9", "3.10", "3.11"])
def tests_cov(session: nox.Session) -> None:
    session.install(".[tests]")

    session.run("coverage", "run", "-m", "pytest", *session.posargs)
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


@nox.session(python="3.9")
def docs(session: nox.Session) -> None:
    # Needs to be separate when using hashes.
    session.install("-r", "requirements/docs.txt")
    session.install("-e", ".")

    if session.posargs:
        session.run("mkdocs", *session.posargs)
    else:
        session.run("mkdocs", "build", "--clean", "--strict")


@nox.session
def pin_docs(session: nox.Session) -> None:
    session.install("pip-tools>=6.8.0")

    session.run(
        "pip-compile",
        "--extra",
        "docs",
        "--index-url",
        "https://pypi.org/simple",
        "--generate-hashes",
        "--resolver",
        "backtracking",
        "--output-file",
        "requirements/docs.txt",
        "pyproject.toml",
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
    # Linux. Since -- unlike on Windows -- you get one binary on both, dynamic
    # standalone ~should be fine~.
    if sys.platform == "win32":
        flavor = "standalone_static"
    else:
        flavor = "standalone"

    session.install("pyoxidizer")

    session.run("pyoxidizer", "-V")
    session.run(
        "pyoxidizer",
        "build",
        "--release",
        "--var",
        "flavor",
        flavor,
        "--var",
        "platform",
        sys.platform,
        env=env,
    )


@nox.session
def pin_for_pyoxidizer(session: nox.Session) -> None:
    """
    Pin the Python dependencies that are used for vendoring by PyOxidizer.
    """
    session.install("pip-tools>=6.8.0")

    session.run(
        "pip-compile",
        "--index-url",
        "https://pypi.org/simple",
        "--generate-hashes",
        "--resolver",
        "backtracking",
        "--output-file",
        f"requirements/pyoxidizer-{sys.platform}.txt",
        "pyproject.toml",
    )
