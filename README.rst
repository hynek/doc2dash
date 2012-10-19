doc2dash: Create docsets for dash
=================================

.. image:: https://secure.travis-ci.org/hynek/doc2dash.png
        :target: https://secure.travis-ci.org/hynek/doc2dash

doc2dash is a MIT licensed extensible `Documentation Set`_ generator
intended to be used with the dash_ API browser for OS X.

If you’ve never heard of dash, you’re missing out: Together with doc2dash it’s
all your API documentation at your fingertips!


Supported input types
---------------------

Currently, the following source types are supported:

- Sphinx_’s HTML output (nearly every single Python project out there)
- pydoctor_’s HTML output (Twisted_!)

Feel free to help adding more! While doc2dash is implemented in Python, the
scope for the supported documentation types is unlimited.  So go on and submit
a parser for your favourite Ruby, Haskell, Lisp, Erlang, JavaScript, ...
format!


Usage
-----

The usage is as simple as: ::

   $ doc2dash -A <docdir>

doc2dash will create a new directory called “<docdir>.docset” in
`~/Library/Application Support/doc2dash/DocSets` containing a dash-compatible
docset with a SQLite_ index. When finished, the docset is automatically added
to dash.

Full usage: ::

   usage: doc2dash [-h] [--force] [--name NAME] [--version] [--quiet] [--verbose]
                [--destination DESTINATION] [--add-to-dash] [-A]
                source

   positional arguments:
     source                Source directory containing API documentation in a
                           supported format.

   optional arguments:
     -h, --help            show this help message and exit
     --force, -f           force overwriting if destination already exists
     --name NAME, -n NAME  name docset explicitly
     --version             show program's version number and exit
     --quiet, -q           limit output to errors and warnings
     --verbose, -v         be verbose
     --destination DESTINATION, -d DESTINATION
                           destination directory for docset (default is current),
                           ignored if -A is specified
     --add-to-dash, -a     automatically add resulting docset to dash
     -A                    create docset in doc2dash's default directory and add
                           resulting docset to dash
     --icon ICON, -i ICON  add PNG icon to docset


Installation
------------

The latest stable version can be always found on PyPI and can therefore be
installed using a simple: ::

   $ pip install --user doc2dash

If you haven’t pip_ yet, installation should be as easy as: ::

   $ curl https://raw.github.com/pypa/pip/master/contrib/get-pip.py | python

doc2dash is tested both under Python 3.2 and Python 2.7. Support for older
Python releases won’t be added.



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
