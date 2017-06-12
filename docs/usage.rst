Usage
=====

The usage is as simple as::

   $ doc2dash -A <docdir>

``doc2dash`` will create a new directory called ``<docdir>.docset`` in ``~/Library/Application Support/doc2dash/DocSets`` containing a Dash.app-compatible docset.
When finished, the docset is automatically added to Dash.app.


Options and Arguments
---------------------

The full usage is::

   $ doc2dash [OPTIONS] SOURCE

The ``SOURCE`` is a directory containing the documentation you would like to convert.
Valid ``OPTIONS`` are the following:

.. option:: -n, --name

   Name the docset explicitly instead of letting doc2dash guess the correct name from the directory name of the source.

.. option:: -d PATH, --destination PATH

   Put the resulting docset into ``PATH``.
   Default is the current directory.
   Ignored if ``--add-to-global`` is specified.

.. option:: -f, --force

   Overwrite docset if it already exists.
   Otherwise, ``doc2dash`` would exit with an error.

.. option:: -i FILENAME, --icon FILENAME

   Add PNG icon ``FILENAME`` to docset that is used within Dash.app to represent the docset.

.. option:: -I FILENAME, --index-page FILENAME

   Set the file that is shown when the docset is clicked within Dash.app.

.. option:: -a, --add-to-dash

   Automatically add the resulting docset to Dash.app.
   Works only on macOS and when Dash.app is installed.

.. option:: -A, --add-to-global

   Create docset in doc2dash's default global directory [``~/Library/Application Support/ doc2dash/DocSets``] and add it to Dash.app
   Works only on macOS and when Dash.app is installed.

.. option:: -j, --enable-js

    Enable bundled and external javascript.

.. option:: -u, --online-redirect-url

    As of Dash 3.0 users can open the online version of pages from within docsets.
    To enable this, you must set this value to the base URL of your online documentation.
    e.g. ``https://doc2dash.readthedocs.io/``

.. option:: --parser

    Specify a the import path of a custom parser class (implementing the ``doc2dash.parsers.utils.IParser`` interface) to use.
    For example, ``--parser doc2dash.parsers.intersphinx.InterSphinxParser`` will use the default ``InterSphinxParser``.
    Default behavior is to auto-detect documentation type.

.. option:: -q, --quiet

   Limit output to errors and warnings.

.. option:: -v, --verbose

   Be verbose.

.. option:: --version

   Show the version and exit.

.. option:: --help

   Show a brief usage summary and exit.
