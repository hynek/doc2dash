================================================
doc2dash: Create docsets for Dash.app and clones
================================================

Release v\ |release| (:doc:`What's new? <changelog>`).


.. include:: ../README.rst
      :start-after: begin


Supported Input Formats
=======================

Currently, the following input formats are supported:

- Sphinx_’s HTML output (nearly every single Python project out there)
- pydoctor_’s HTML output (Twisted_!)

Feel free to help adding more! While ``doc2dash`` is implemented in Python, the scope for the supported documentation types is unlimited.
So go on and submit a parser for your favourite Ruby, Haskell, Lisp, Erlang, JavaScript, …  format!


User's Guide
============

.. toctree::
   :maxdepth: 1

   installation
   usage


Project Information
-------------------

.. toctree::
   :maxdepth: 1

   changelog
   license
   contributing


Indices and tables
==================

* :ref:`genindex`
* :ref:`search`

.. _Twisted: https://twistedmatrix.com/
.. _pydoctor: https://launchpad.net/pydoctor
.. _Sphinx:  http://sphinx-doc.org/
