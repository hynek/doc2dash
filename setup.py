from __future__ import absolute_import, division, print_function

import codecs
import os
import re

from setuptools import setup, find_packages


###############################################################################

NAME = "doc2dash"
INSTALL_REQUIRES = [
    "Sphinx==1.6.2",
    "attrs==17.2.0",
    "beautifulsoup4==4.6.0",
    "click==6.7",
    "colorama==0.3.9",
    "lxml==3.8.0",
    "six==1.10.0",
    "zope.interface==4.4.1",
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


VERSION = find_meta("version")
URI = find_meta("url")
LONG = (
    read("README.rst") + "\n\n" +
    "Release Information\n" +
    "===================\n\n" +
    re.search("(\d+.\d.\d \(.*?\)\n.*?)\n\n\n----\n\n\n",
              read("CHANGELOG.rst"), re.S).group(1) +
    "\n\n`Full changelog " +
    "<{uri}en/stable/changelog.html>`_.\n\n" + read("AUTHORS.rst")
).format(uri=URI)


if __name__ == "__main__":
    setup(
        name=NAME,
        version=VERSION,
        description=find_meta("description"),
        long_description=LONG,
        url=URI,
        license=find_meta("license"),
        author=find_meta("author"),
        author_email=find_meta("email"),
        packages=find_packages(where="src"),
        package_dir={"": "src"},
        entry_points=ENTRY_POINTS,
        install_requires=INSTALL_REQUIRES,
        classifiers=CLASSIFIERS,
    )
