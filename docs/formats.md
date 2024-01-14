# Supported Input Formats

## intersphinx

*intersphinx* is a way to store API metadata along with any type of HTML documentation.
Originally conceived to ease inter-project API linking, it's been an [extension to *Sphinx*](https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html) for many years now.

You can recognize *intersphinx*-based docs by the `objects.inv` file at the root of the built documentation.

The most common documentation formats that support *intersphinx* are:

- [Sphinx](https://www.sphinx-doc.org/), a very common documentation framework in the Python world and beyond.
- [MkDocs](https://www.mkdocs.org/), **if** used with the [*mkdocstrings*](https://mkdocstrings.github.io) plugin.
- [*pydoctor*](https://github.com/twisted/pydoctor) since version 21.2.0[^pydoctor].

If you find a documentation format that supports *intersphinx* but yields poor results from *doc2dash*, please [let us know](https://github.com/hynek/doc2dash/issues).

> [!WARNING]
> Do **not** attempt to run *doc2dash* over pre-built HTML documentation downloaded from [*Read The Docs*](https://readthedocs.org).
> Those downloads aren't direct equivalents of the actual, pristine builds and indexing will not work.

[^pydoctor]:
    Dedicated support for *pydoctor* has been removed after it became *intersphinx*-compatible.
    If you need to convert legacy *pydoctor* documentation, please use [*doc2dash* 2.4.1](https://pypi.org/project/doc2dash/2.4.1/).
