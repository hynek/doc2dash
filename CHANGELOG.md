# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!-- changelog follows -->

## [3.1.0](https://github.com/hynek/doc2dash/compare/3.0.0...3.1.0) - 2024-01-15

### Added

- Support for high resolution icons using the `--icon-2x` option.
  [#200](https://github.com/hynek/doc2dash/pull/200)

- Support for linking to [docset playgrounds](https://kapeli.com/docsets#docsetPlaygrounds) using the `--playground-url` option.
  [#201](https://github.com/hynek/doc2dash/pull/201)

- Control over [full-text search](https://kapeli.com/docsets#fts) using the `--full-text-search=(on|off|forbidden)` option.
  [#202](https://github.com/hynek/doc2dash/pull/202)


### Fixed

- The table of contents-generation for *pydoctor*-based documentation has been restored.
  [#133](https://github.com/hynek/doc2dash/pull/133)


## [3.0.0](https://github.com/hynek/doc2dash/compare/2.4.1...3.0.0) - 2022-09-13

### Removed

- Since *pydoctor* added support for *intersphinx* in version 21.2.0, the dedicated HTML-parsing parser has been removed. If you need to parse legacy *pydoctor* docs, please use *doc2dash* 2.4.1.


### Added

- Stand-alone binaries! If your platform is supported, you can now download binaries from the release page without dealing with Python at all – courtesy of [*PyOxidizer*](https://pyoxidizer.readthedocs.io/).
- *intersphinx*: documentation based on [*MkDocs*](https://www.mkdocs.org/) with [*mkdocstrings*](https://mkdocstrings.github.io/) metadata is now supported.
- *intersphinx*: if no explicit name is passed, the docset name is derived von the documentation's metadata (and not the directory name, which is more often than not just `html`).
- We use [*rich*](https://rich.readthedocs.io/) for output and progress bars now. This allows us more granular progress indication.
- Documentation on writing your own parser plugins.


### Changed

- Tons of refactorings that probably broke your custom parsers. Sorry about that and let us know, if we can help you fixing them.
- *intersphinx*: We now parse `objects.inv` files on our own. *Sphinx* is not a dependency anymore.
- *intersphinx*: Files that are indexed by *intersphinx*, but don't exist aren't added to the docset anymore. Common example is `py-modindex.html`. [#113](https://github.com/hynek/doc2dash/issues/113) [#115](https://github.com/hynek/doc2dash/issues/115)
- We now check if the index page passed via `--index-page` / `-I` exists and fail if it doesn't.


## [2.4.1](https://github.com/hynek/doc2dash/compare/2.4.0...2.4.1) - 2022-01-21

### Added

- Added support for URL-encoded filenames. [\#104](https://github.com/hynek/doc2dash/pull/104)


## [2.4.0](https://github.com/hynek/doc2dash/compare/2.3.0...2.4.0) - 2021-11-16

### Removed

- Every Python version older than 3.8. Please use 2.3 if you need to run *doc2dash* on legacy Python versions.

### Added

- Better display names with Sphinx v2 inventories. [\#101](https://github.com/hynek/doc2dash/pull/101)

- *intersphinx*: new types:

  - `cmdoption` (deprecated alias for `option`)
  - `doc`
  - `label`
  - `property`
  - `protocol`
  - `setting`
  - `term`

  Re-indexing your documentation may add new index entries!


### Changed

- `zope.interface` is not a dependency anymore.
- `colorama` is only a dependency on Windows now.


### Fixed

- Work around a display bug in older Dash releases by setting the plist key `DashDocSetDeclaredInStyle` to `originalName`.


## [2.3.0](https://github.com/hynek/doc2dash/compare/2.2.0...2.3.0) - 2018-11-24

### Deprecated

- This is the **final release** that works on Python versions older than 3.8. If necessary, there *may* be more 2.3.x bugfix releases -- the next release will **require Python 3.8** or later though.


### Changed

- The dependencies aren't pinned anymore.
- `lxml` is not a dependency anymore.

### Fixed

- `python -m doc2dash` works now as expected.


## [2.2.0](https://github.com/hynek/doc2dash/compare/2.1.0...2.2.0) - 2017-06-12

### Added

- `InterSphinxParser` is now open to extension. [\#59](https://github.com/hynek/doc2dash/pull/59)
- Support a `--parser` option to force the use of a custom parser class. [\#60](https://github.com/hynek/doc2dash/pull/60)


## [2.1.0](https://github.com/hynek/doc2dash/compare/2.0.2...2.1.0) - 2016-03-14

### Removed

- Remove legacy Sphinx parsing. The intersphinx parser is much more robust so the old way shouldn't be needed anymore.


### Added

- Add support for InterSphinx constants. [\#49](https://github.com/hynek/doc2dash/pull/49)
- Add support for `--enable-js` and `--online-redirect-url` options. [\#43](https://github.com/hynek/doc2dash/issues/43)


### Fixed

- Fix handling in-docs links with multiple anchors. [\#47](https://github.com/hynek/doc2dash/issues/47)
- Better support for relative paths. [\#37](https://github.com/hynek/doc2dash/issues/37), [\#41](https://github.com/hynek/doc2dash/issues/41)


## [2.0.2](https://github.com/hynek/doc2dash/compare/2.0.1...2.0.2) - 2014-09-24

### Fixed

- Detection of [pydoctor 0.5](http://bazaar.launchpad.net/~mwhudson/pydoctor/dev/revision/605). [\#31](https://github.com/hynek/doc2dash/issues/31), [\#39](https://github.com/hynek/doc2dash/issues/39)


## [2.0.1](https://github.com/hynek/doc2dash/compare/2.0.0...2.0.1) - 2014-09-16

### Fixed

- Better Unicode support. The move from `unicode_literals` to explicit prefixes broke some things that are fixed now. [\#29](https://github.com/hynek/doc2dash/issues/29), [\#30](https://github.com/hynek/doc2dash/issues/30)


## [2.0.0](https://github.com/hynek/doc2dash/compare/1.2.1...2.0.0) - 2014-08-14

### Added

- Added a new parser for Sphinx documentation that uses [intersphinx](https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html) files that are machine readable. That should lead to more reliable parsing and a better deduction of symbol types. [\#28](https://github.com/hynek/doc2dash/issues/28)
- Added Sphinx-based documentation.
- Added colors, styles, and a progress bar to make output more comprehensible.

### Changed

- Internally quite a few changes happened. Most prominently tuples and namedtuples have been replaced by real classes and parsers don't inherit from anything anymore. The fundamental working principal stayed the same though so porting your parsers is trivial.

### Fixed

- `setup.py test` works now.


## [1.2.1](https://github.com/hynek/doc2dash/compare/1.2.0...1.2.1) - 2014-07-24

### Fixed

- Fix docset name deduction if the source path ends with a `/`. [\#26](https://github.com/hynek/doc2dash/issues/26)


## [1.2.0](https://github.com/hynek/doc2dash/compare/1.1.0...1.2.0) - 2014-01-07

### Added

- Runs now on Python 3.3. This is achieved by upgrading dependencies that didn't play along well before on 3.3.
- Add `--index` option.


## [1.1.0](https://github.com/hynek/doc2dash/compare/1.0.0...1.1.0) - 2013-01-13

## Fixed

- Use better Dash types for modules and attributes.


## [1.0.0](https://github.com/hynek/doc2dash/compare/0.3.1...1.0.0) - 2012-10-14

### Changed
- Due to lack of known problems, pronouncing stable, thus 1.0.0.
- Please note that no code except for the tests has changed since 0.3.1.


### Fixed
- Make tests pass on Python 2.7 too.


## [0.3.1](https://github.com/hynek/doc2dash/compare/0.3.0...0.3.1) - 2012-06-28

### Changed

- Pronounced beta – happy testing!


## [0.3.0](https://github.com/hynek/doc2dash/compare/0.2.2...0.3.0) - 2012-06-28

### Added

- Add table of contents links to docs to get a nice TOC in Dash when inside of a module.
- Support `DashDocSetFamily` field.
- Add `--verbose` and `--quiet` options.
- Add `--destination` option.
- Add `--add-to-dash` option.
- Allow adding of an PNG icon to the docset (`--icon`).


## [0.2.2](https://github.com/hynek/doc2dash/compare/0.2.1...0.2.2) - 2012-06-16

### Changed

- Don't collect () as part of method/function names.
- Index whole names: symbols are searchable by the whole name, including the namespace.


## [0.2.1](https://github.com/hynek/doc2dash/compare/0.2.1...0.2.0) - 2012-06-15

### Fixed

- Fix PyPI package: add missing MANIFEST.in and add missing packages to setup.py.


## [0.2.0](https://github.com/hynek/doc2dash/tree/0.2.0) - 2012-06-14

### Added

- Add support for built-in constants and classes.

### Changed

- Strip annotations from unused remembered names the are re-used in synonyms.
