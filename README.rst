doc2dash: Create docsets for dash
=================================

doc2dash is a MIT licensed extensible `Documentation Set`_ generator
intended to be used with the dash_ API browser for OS X.

It’s proudly written in `Python 3`_.

Supported input types
---------------------

Currently, the following source types are supported:

- Sphinx_ (nearly every single Python project out there)
- pydoctor_ (Twisted_)

Feel free to help adding more!


Usage
-----

The usage is a simple as: ::

   $ doc2dash <docdir>

doc2dash will create a new directory called “<docdir>.docset” in the current
directory containing a dash-compatible docset with a SQLite_ index.

When finished, the docset can be imported into dash.

Full usage: ::

   usage: doc2dash [-h] [--force] [--name NAME] [--version] source

   Convert docs to docsets.

   positional arguments:
     source                Source directory containing API documentation in a
                           supported format.

   optional arguments:
     -h, --help            show this help message and exit
     --force, -f           force overwriting if destination already exists
     --name NAME, -n NAME  name docset explicitly
     --version             show program's version number and exit


Installation
------------

The latest stable version can be always found on PyPI and can therefore be
installed using a simple: ::

   $ pip-3.2 install --user doc2dash

The easiest way known to me to get Python 3.2 on OS X is using homebrew_: ::

   $ brew install python3

The installation of pip_ should be as easy as: ::

   $ curl https://raw.github.com/pypa/pip/master/contrib/get-pip.py | python3.2



.. _`Documentation Set`: https://developer.apple.com/library/mac/#documentation/DeveloperTools/Conceptual/Documentation_Sets/000-Introduction/introduction.html
.. _dash: http://kapeli.com/dash/
.. _`Python 3`: http://getpython3.com/
.. _pydoctor: http://codespeak.net/~mwh/pydoctor/
.. _Sphinx: http://sphinx.pocoo.org/
.. _SQLite: http://www.sqlite.org/
.. _PyPI: http://pypi.python.org/pypi/doc2dash/
.. _Twisted: http://twistedmatrix.com/
.. _homebrew: http://mxcl.github.com/homebrew/
.. _pip: http://www.pip-installer.org/en/latest/installing.html#alternative-installation-procedures
