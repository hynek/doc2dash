Supported Input Formats
=======================

Currently, ``doc2dash`` supports two documentation formats:

- :ref:`Sphinx-sec`
- :ref:`pydoctor-sec`

Feel free to help adding more! While ``doc2dash`` is implemented in Python, the scope for the supported documentation types is unlimited.
So go on and submit a parser for your favourite Ruby, Haskell, Lisp, Erlang, JavaScript, …  format!


.. _Sphinx-sec:

Sphinx
------

Sphinx_ is a very common documentation format in the Python world and beyond.

``doc2dash`` offers two approaches to parsing it.
The preferable one is used whenever a machine-readable intersphinx_ index file is present and it results in very precise and reliable parsing.

If none is found, ``doc2dash`` attempts to parse the HTML API index file (``genindex.html`` or ``genindex-all.html``).  
Simply point ``doc2dash`` at Sphinx's HTML output (usually ``_build/html`` if you built it yourself) and it will do the right thing.


.. _pydoctor-sec:

pydoctor
--------

Contrary to Sphinx, pydoctor_ is not a complete documentation format.
Instead, it's focused on creating API documentation from Python docstrings.
The most popular project employing is Twisted_ and its ecosystem.

Since pydoctor alas does not emit a machine-readable file, the ``nameIndex.html`` is always parsed.
Fortunately, no theming is common in the pydoctor world, so the parsing is reliable nonetheless.


.. _Twisted: https://twistedmatrix.com/
.. _pydoctor: https://launchpad.net/pydoctor
.. _Sphinx:  http://sphinx-doc.org/
.. _intersphinx: http://sphinx-doc.org/latest/ext/intersphinx.html
