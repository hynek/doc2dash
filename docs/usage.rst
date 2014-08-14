Usage
=====

The usage is as simple as::

   $ doc2dash -A <docdir>

``doc2dash`` will create a new directory called ``<docdir>.docset`` in ``~/Library/Application Support/doc2dash/DocSets`` containing a dash-compatible docset with a SQLite_ index.
When finished, the docset is automatically added to dash.

Full usage: ::

   Usage: doc2dash [OPTIONS] SOURCE

   Convert docs from SOURCE to Dash.app's docset format.

   Options:
   -f, --force                force overwriting if destination already exists
   -n, --name NAME            name docset explicitly
   -q, --quiet                limit output to errors and warnings
   -v, --verbose              be verbose
   -d, --destination PATH     destination directory for docset, ignored if -A
                              is specified  [default: .]
   -a, --add-to-dash          automatically add resulting docset to Dash.app
   -A, --add-to-global        create docset in doc2dash's default global
                              directory [~/Library/Application Support/
                              doc2dash/DocSets] and add it to Dash.app
   -i, --icon FILENAME        add PNG icon to docset
   -I, --index-page FILENAME  set the file that is shown when the docset is
                              clicked within Dash.app
   --version                  Show the version and exit.
   --help                     Show this message and exit.


Hints
-----
For Sphinx, you get the best results using the intersphinx_ parser that is used automatically if a version 2 ``objects.inv`` file is present.
This approach obviates parsing problems completely by using that machine readable file using Sphinx’s own APIs.

.. _SQLite: http://www.sqlite.org/
