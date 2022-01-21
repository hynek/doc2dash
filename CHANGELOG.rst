.. changelog

Changelog
=========

2.4.1 (2022-01-21)
------------------

- Added support for URL-encoded filenames.
  `#104 <https://github.com/hynek/doc2dash/pull/104>`_


----


2.4.0 (2021-11-16)
------------------

This version dropped every Python version older than 3.8.
Please use 2.3 if you need to run ``doc2dash`` on legacy Python versions.

- Better display names with Sphinx v2 inventories.
  `#101 <https://github.com/hynek/doc2dash/pull/101>`_
- Added new ``intersphinx`` types:

  * ``cmdoption`` (deprecated alias for ``option``)
  * ``doc``
  * ``label``
  * ``property``
  * ``protocol``
  * ``setting``
  * ``term``

  Re-indexing your documentation may add new index entries!

- ``zope.interface`` is not a dependency anymore.
- ``colorama`` is only a dependency on Windows now.
- Work around a display bug in older Dash.app releases by setting the plist key ``DashDocSetDeclaredInStyle`` to ``originalName``.


----


2.3.0 (2018-11-24)
------------------

This is the **final release** that works on Python versions older than 3.8.
If necessary, there *may* be more 2.3.x bugfix releases -- the next release will **require Python 3.8** or later though.

- The dependencies aren't pinned anymore.
- ``lxml`` is not a dependency anymore.
- ``python -m doc2dash`` works now as expected.


----


2.2.0 (2017-06-12)
------------------

- ``InterSphinxParser`` is now open to extension.
  `#59 <https://github.com/hynek/doc2dash/pull/59>`_
- Support a ``--parser`` option to force the use of a custom parser class.
  `#60 <https://github.com/hynek/doc2dash/pull/60>`_


----


2.1.0 (2016-03-14)
------------------

- Remove legacy Sphinx parsing.
  The intersphinx parser is much more robust so the old way shouldn't be needed anymore.
- Add support for InterSphinx constants.
  `#49 <https://github.com/hynek/doc2dash/pull/49>`_
- Fix handling in-docs links with multiple anchors.
  `#47 <https://github.com/hynek/doc2dash/issues/47>`_
- Add support for ``--enable-js`` and ``--online-redirect-url`` options.
  `#43 <https://github.com/hynek/doc2dash/issues/43>`_
- Better support for relative paths.
  `#37 <https://github.com/hynek/doc2dash/issues/37>`_, `#41 <https://github.com/hynek/doc2dash/issues/41>`_


----


2.0.2 (2014-09-24)
------------------

- Fix detection of `pydoctor 0.5 <http://bazaar.launchpad.net/~mwhudson/pydoctor/dev/revision/605>`_.
  `#31 <https://github.com/hynek/doc2dash/issues/31>`_, `#39 <https://github.com/hynek/doc2dash/issues/39>`_


----


2.0.1 (2014-09-16)
------------------

- Better Unicode support.
  The move from ``unicode_literals`` to explicit prefixes broke some things that are fixed now.
  `#29 <https://github.com/hynek/doc2dash/issues/29>`_, `#30 <https://github.com/hynek/doc2dash/issues/30>`_


----


2.0.0 (2014-08-14)
------------------

- Added a new parser for Sphinx documentation that uses `intersphinx <https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html>`_ files that are machine readable.
  That should lead to more reliable parsing and a better deduction of symbol types.
  `#28 <https://github.com/hynek/doc2dash/issues/28>`_
- Added Sphinx-based documentation.
- Added colors, styles, and a progress bar to make output more comprehensible.
- ``setup.py test`` works now.
- Internally quite a few changes happened.
  Most prominently tuples and namedtuples have been replaced by real classes and parsers don't inherit from anything anymore.
  The fundamental working principal stayed the same though so porting your parsers is trivial.


----


1.2.1 (2014-07-24)
------------------

- Fix docset name deduction if the source path ends with a ``/``.
  `#26 <https://github.com/hynek/doc2dash/issues/26>`_


----


1.2.0 (2014-01-07)
------------------

- Runs now on Python 3.3.
  This is achieved by upgrading dependencies that didn't play along well before on 3.3.
- Add ``--index`` option.


----


1.1.0 (2013-01-13)
------------------

- Use better dash types for modules and attributes.


----


1.0.0 (2012-10-14)
------------------

- Make tests pass on Python 2.7 too.
- Due to lack of known problems, pronouncing stable, thus 1.0.0.
- Please note that no code except for the tests has changed since 0.3.1.


----


0.3.1 (2012-06-28)
------------------

- Pronounced beta – happy testing!


----


0.3.0 (2012-06-28)
------------------

- Add table of contents links to docs to get a nice TOC in dash when inside of a module.
- Support DashDocSetFamily field.
- Add ``--verbose`` and ``--quiet`` options.
- Add ``--destination`` option.
- Add ``--add-to-dash`` option.
- Allow adding of an PNG icon to the docset (``--icon``).


----


0.2.2 (2012-06-16)
------------------

- Don't collect () as part of method/function names.
- Index whole names: symbols are searchable by the whole name, including the namespace.


----


0.2.1 (2012-06-15)
------------------

- Fix PyPI package: add missing MANIFEST.in and add missing packages to setup.py.


----


0.2.0 (2012-06-14)
------------------

- Add support for built-in constants and classes.
- Strip annotations from unused remembered names the are re-used in synonyms.
