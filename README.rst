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


Installation
------------

The latest stable version can be always found on PyPI and can therefore be
installed using a simple: ::

   $ pip install --user doc2dash



.. _`Documentation Set`: https://developer.apple.com/library/mac/#documentation/DeveloperTools/Conceptual/Documentation_Sets/000-Introduction/introduction.html   
.. _dash: http://kapeli.com/dash/
.. _`Python 3`: http://getpython3.com/
.. _pydoctor: http://codespeak.net/~mwh/pydoctor/
.. _Sphinx: http://sphinx.pocoo.org/
.. _SQLite: http://www.sqlite.org/
.. _PyPI: http://pypi.python.org/pypi/doc2dash/
.. _Twisted: http://twistedmatrix.com/
