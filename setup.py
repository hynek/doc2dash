import re

from pathlib import Path

from setuptools import find_packages, setup


###############################################################################

NAME = "doc2dash"
PYTHON_REQUIRES = ">=3.8"
INSTALL_REQUIRES = [
    "Sphinx",
    "attrs",
    "beautifulsoup4",
    "click",
    "colorama; platform_system=='Windows'",
]
EXTRAS_REQUIRE = {"tests": ["coverage[toml]", "pytest"], "docs": ["furo"]}
EXTRAS_REQUIRE["dev"] = (
    EXTRAS_REQUIRE["tests"] + EXTRAS_REQUIRE["docs"] + ["pre-commit"]
)

PROJECT_URLS = {
    "Changelog": "https://doc2dash.readthedocs.io/en/stable/changelog.html",
    "Documentation": "https://doc2dash.readthedocs.io/",
    "Bug Tracker": "https://github.com/hynek/doc2dash/issues",
    "Source Code": "https://github.com/hynek/doc2dash",
    "Funding": "https://github.com/sponsors/hynek",
    "Ko-fi": "https://ko-fi.com/the_hynek",
}

ENTRY_POINTS = {"console_scripts": ["doc2dash = doc2dash.__main__:main"]}
CLASSIFIERS = [
    "Development Status :: 5 - Production/Stable",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: MacOS :: MacOS X",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: POSIX",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: Implementation :: CPython",
    "Programming Language :: Python",
    "Topic :: Documentation",
    "Topic :: Software Development :: Documentation",
    "Topic :: Software Development",
    "Topic :: Text Processing",
]

###############################################################################


here = Path(__file__).resolve().parent

META_PATH = here / "src" / NAME / "__init__.py"
META_FILE = META_PATH.read_text()


def read(path: Path) -> str:
    return (here / path).read_text()


def find_meta(meta: str) -> str:
    """
    Extract __*meta*__ from META_FILE.
    """
    meta_match = re.search(
        fr"^__{meta}__ = ['\"]([^'\"]*)['\"]", META_FILE, re.M
    )
    if meta_match:
        return meta_match.group(1)

    raise RuntimeError(f"Unable to find __{meta}__ string.")


VERSION = find_meta("version")
URL = find_meta("url")
LONG = (
    read("README.rst").split(".. begin\n")[1]
    + "\n\n"
    + "Release Information\n"
    + "===================\n\n"
    + re.search(
        r"(\d+.\d.\d \(.*?\)\n.*?)\n\n\n----\n\n\n",
        read("CHANGELOG.rst"),
        re.S,
    ).group(1)
    + "\n\n`Full changelog "
    + f"<{URL}en/stable/changelog.html>`_.\n\n"
    + read("AUTHORS.rst")
)


if __name__ == "__main__":
    setup(
        name=NAME,
        version=VERSION,
        description=find_meta("description"),
        long_description=LONG,
        long_description_content_type="text/x-rst",
        url=URL,
        project_urls=PROJECT_URLS,
        license=find_meta("license"),
        author=find_meta("author"),
        author_email=find_meta("email"),
        packages=find_packages(where="src"),
        package_dir={"": "src"},
        entry_points=ENTRY_POINTS,
        python_requires=PYTHON_REQUIRES,
        install_requires=INSTALL_REQUIRES,
        extras_require=EXTRAS_REQUIRE,
        classifiers=CLASSIFIERS,
        options={"bdist_wheel": {"universal": "1"}},
    )
