import codecs
import os
import re
import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    """
    Build an absolute path from *parts* and and return the contents of the
    resulting file.  Assume UTF-8 encoding.
    """
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, *parts), "rb", "utf-8") as f:
        return f.read()


def find_version(*file_paths):
    """
    Build a path from *file_paths* and search for a ``__version__``
    string inside.
    """
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = None

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, because outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args or [] +
                            ["tests"])
        sys.exit(errno)


setup(
    name='doc2dash',
    version=find_version('doc2dash', '__init__.py'),
    description="Convert docs to Dash.app's docset format.",
    long_description=read('README.rst'),
    url='http://github.com/hynek/doc2dash/',
    license='MIT',
    author='Hynek Schlawack',
    author_email='hs@ox.cx',
    packages=find_packages(exclude=['tests*']),
    entry_points={
        'console_scripts': [
            'doc2dash = doc2dash.__main__:main',
        ],
    },
    install_requires=[
        "Sphinx>=1.2.3",
        "beautifulsoup4>=4.3.2",
        "characteristic>=14.2.0",
        "click>=3.3",
        "colorama>=0.3.2",
        "lxml>=3.4.0",
        "six>=1.8.0",
        "zope.interface>=4.1.1",
    ],
    tests_require=[
        "pytest",
    ],
    cmdclass={
        "test": PyTest,
    },
    classifiers=[
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
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Programming Language :: Python",
        "Topic :: Documentation",
        "Topic :: Software Development :: Documentation",
        "Topic :: Software Development",
        "Topic :: Text Processing",
    ],
)
