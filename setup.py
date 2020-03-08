import re

from pathlib import Path

from setuptools import find_packages, setup


###############################################################################

NAME = "doc2dash"
INSTALL_REQUIRES = ["Sphinx", "attrs", "beautifulsoup4", "click", "colorama"]
EXTRAS_REQUIRE = {"tests": ["coverage", "pytest"]}
EXTRAS_REQUIRE["dev"] = EXTRAS_REQUIRE["tests"] + ["pre-commit"]

PROJECT_URLS = {
    "Documentation": "https://doc2dash.readthedocs.io/",
    "Bug Tracker": "https://github.com/hynek/doc2dash/issues",
    "Source Code": "https://github.com/hynek/doc2dash",
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
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
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
        r"^__%s__ = ['\"]([^'\"]*)['\"]" % (meta,), META_FILE, re.M
    )
    if meta_match:
        return meta_match.group(1)

    raise RuntimeError("Unable to find __%s__ string." % (meta,))


VERSION = find_meta("version")
URL = find_meta("url")
LONG = (
    read("README.rst")
    + "\n\n"
    + "Release Information\n"
    + "===================\n\n"
    + re.search(
        r"(\d+.\d.\d \(.*?\)\n.*?)\n\n\n----\n\n\n",
        read("CHANGELOG.rst"),
        re.S,
    ).group(1)
    + "\n\n`Full changelog "
    + "<%sen/stable/changelog.html>`_.\n\n" % (URL,)
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
        install_requires=INSTALL_REQUIRES,
        extras_require=EXTRAS_REQUIRE,
        classifiers=CLASSIFIERS,
    )
