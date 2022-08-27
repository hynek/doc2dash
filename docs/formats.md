# Supported Input Formats

*doc2dash* supports two documentation formats:
*Sphinx* and *pydoctor*

I would **love** to add more formats!
While *doc2dash* is implemented in Python, the scope for the supported documentation types is unlimited.
Please reach out if you're interested helping!


## Sphinx

[*Sphinx*](https://www.sphinx-doc.org/) is a very common documentation framework in the Python world and beyond.

*doc2dash* uses the machine-readable `objects.inv` file (`intersphinx`) to determine the symbols and patches the documentation such that *Dash.app* can link to them.

---

The trickiest part of building *Sphinx* documentation for a project is figuring out the dependencies necessary.
Be on the lookout for `docs` extras or files called like `docs-requirements.txt` et cetera.

Once that's set up, building *Sphinx* documentation is usually straight-forward:
change into their documentation directory (usually `docs` or `doc`) and run `make html`.

!!! Warning

    Do **not** attempt to run *doc2dash* over pre-built HTML documentation downloaded from [*Read The Docs*](https://readthedocs.org).
    Those downloads aren't direct equivalents of the actual, pristine builds and indexing will not work.


## pydoctor

Unlike *Sphinx*, [*pydoctor*](https://github.com/twisted/pydoctor) is not a complete documentation format.
Instead, it's focused on creating API documentation from Python docstrings.
The most popular project employing it being [Twisted](https://twistedmatrix.com/) and its ecosystem.

Since *pydoctor* alas does not emit a machine-readable file, the `nameIndex.html` file is parsed.
Fortunately, no theming is common in the *pydoctor* world, so the parsing is reliable nonetheless.
