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

Building Sphinx documentation is usually easy:
after installing the ``sphinx`` package, ``cd`` into their documentation directory (usually ``docs`` or ``doc``) and enter ``make html``.

.. warning::

   Do **not** attempt to run ``doc2dash`` over pre-built HTML documentation downloaded from Read The Docs.
   Those downloads aren't direct equivalents of the actual, pristine builds and indexing will not work.



.. _pydoctor-sec:

pydoctor
--------

Contrary to Sphinx, pydoctor_ is not a complete documentation format.
Instead, it's focused on creating API documentation from Python docstrings.
The most popular project employing is Twisted_ and its ecosystem.

Since pydoctor alas does not emit a machine-readable file, the ``nameIndex.html`` is parsed.
Fortunately, no theming is common in the pydoctor world, so the parsing is reliable nonetheless.


.. _Twisted: https://twistedmatrix.com/
.. _pydoctor: https://launchpad.net/pydoctor
.. _Sphinx:  http://sphinx-doc.org/
