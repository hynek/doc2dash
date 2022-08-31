# Supported Input Formats

Additionally to the formats below, I would **love** to add more formats!
While *doc2dash* is implemented in Python, the scope for the supported documentation types is unlimited.
Please reach out if you're interested helping!


## intersphinx

*intersphinx* is not a format, but a way to store API metadata along with any type of HTML documentation.
Originally conceived to ease inter-project API linking, it's been an [extension to *Sphinx*](https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html) for many years now.

You can recognize *intersphinx*-based docs by the `objects.inv` file at the root of the built documentation.

The most common documentation formats that support *intersphinx* are:

- [*Sphinx*](https://www.sphinx-doc.org/), a very common documentation framework in the Python world and beyond.
- [*MkDocs*](https://www.mkdocs.org/), **if** used with the [*mkdocstrings*](https://mkdocstrings.github.io) plugin.

!!! Warning

    Do **not** attempt to run *doc2dash* over pre-built HTML documentation downloaded from [*Read The Docs*](https://readthedocs.org).
    Those downloads aren't direct equivalents of the actual, pristine builds and indexing will not work.


## pydoctor

[*pydoctor*](https://github.com/twisted/pydoctor) is focused on creating API documentation from Python docstrings.
The most popular project employing it being [Twisted](https://twistedmatrix.com/) and its ecosystem.

Since *pydoctor* does not emit a machine-readable file, the `nameIndex.html` file is parsed.
Fortunately, no theming is common in the *pydoctor* world, so the parsing is reliable nevertheless.
