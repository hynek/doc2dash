from __future__ import absolute_import, division, print_function

import codecs
import os
import re

from setuptools import setup, find_packages


###############################################################################

NAME = "doc2dash"
INSTALL_REQUIRES = [
    "Sphinx==1.3.1",
    "beautifulsoup4==4.4.0",
    "characteristic==14.3.0",
    "click==5.1",
    "colorama==0.3.3",
    "lxml==3.4.4",
    "six==1.9.0",
    "zope.interface==4.1.2",
]
ENTRY_POINTS = {
    "console_scripts": [
        "doc2dash = doc2dash.__main__:main",
    ],
}
CLASSIFIERS = [
    "Development Status :: 5 - Production/Stable",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: MacOS :: MacOS X",
    "Operating System :: POSIX",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: Implementation :: CPython",
    "Programming Language :: Python :: Implementation :: PyPy",
    "Programming Language :: Python",
    "Topic :: Documentation",
    "Topic :: Software Development :: Documentation",
    "Topic :: Software Development",
    "Topic :: Text Processing",
]

###############################################################################


here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    """
    Build an absolute path from *parts* and and return the contents of the
    resulting file.  Assume UTF-8 encoding.
    """
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, *parts), "rb", "utf-8") as f:
        return f.read()

try:
    META_PATH
except NameError:
    META_PATH = os.path.join(here, "src", NAME, "__init__.py")

META_FILE = read(META_PATH)


def find_meta(meta):
    """
    Extract __*meta*__ from META_FILE.
    """
    meta_match = re.search(
        r"^__{meta}__ = ['\"]([^'\"]*)['\"]".format(meta=meta),
        META_FILE, re.M
    )
    if meta_match:
        return meta_match.group(1)
    raise RuntimeError("Unable to find __{meta}__ string.".format(meta=meta))


if __name__ == "__main__":
    setup(
        name=NAME,
        version=find_meta("version"),
        description=find_meta("description"),
        long_description=(
            read("README.rst") + "\n\n" +
            read("AUTHORS.rst") + "\n\n" +
            read("CHANGELOG.rst")
        ),
        url=find_meta("url"),
        license=find_meta("license"),
        author=find_meta("author"),
        author_email=find_meta("email"),
        packages=find_packages(where="src"),
        package_dir={"": "src"},
        entry_points=ENTRY_POINTS,
        install_requires=INSTALL_REQUIRES,
        classifiers=CLASSIFIERS,
    )
