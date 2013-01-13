.. :changelog:

History
=======

1.1.0 (2013-01-13)
------------------

- Use better dash types for modules and attributes.

1.0.0 (2012-10-14)
------------------

- Make tests pass on Python 2.7 too.
- Due to lack of known problems, pronouncing stable, thus 1.0.0.
- Please note that no code except for the tests has changed since 0.3.1.

0.3.1 (2012-06-28)
------------------

- Pronounced beta – happy testing!

0.3.0 (2012-06-28)
------------------

- Add table of contents links to docs to get a nice TOC in dash when inside of
  a module.
- Support DashDocSetFamily field.
- Add `--verbose` and `--quiet` options.
- Add `--destination` option.
- Add `--add-to-dash` option.
- Allow adding of an PNG icon to the docset (`--icon`).

0.2.2 (2012-06-16)
------------------

- Don't collect () as part of method/function names.
- Index whole names: symbols are searchable by the whole name, including the
  namespace.


0.2.1 (2012-06-15)
------------------

- Fix pypi package: add missing MANIFEST.in and add missing packages to
  setup.py.


0.2.0 (2012-06-14)
------------------

- Add support for built-in constants and classes.
- Strip annotations from unused remembered names the are re-used in synonyms.
