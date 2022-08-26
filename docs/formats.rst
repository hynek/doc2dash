Supported Input Formats
=======================

Currently, ``doc2dash`` supports two documentation formats:

- :ref:`Sphinx-sec`
- :ref:`pydoctor-sec`

Feel free to help adding more! While ``doc2dash`` is implemented in Python, the scope for the supported documentation types is unlimited.

.. _Sphinx-sec:

Sphinx
------

Sphinx_ is a very common documentation framework in the Python world and beyond.

`doc2dash` uses the machine-readable `objects.inv` file (`intersphinx`) to determine the symbols and patches the documentation such that Dash.app can link to them.

-----

Building Sphinx documentation is usually straight-forward:
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
.. _pydoctor: https://github.com/twisted/pydoctor
.. _Sphinx: https://www.sphinx-doc.org/
