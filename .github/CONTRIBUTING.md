# How To Contribute

Every open source project lives from the generous help by contributors that sacrifice their time and *doc2dash* is no different.

Here are a few guidelines to get you started:

- No contribution is too small; please submit as many fixes for typos and grammar bloopers as you can!

- Try to limit each pull request to one change only.

- To run the test suite, all you need is a recent [Nox](https://nox.thea.codes/).
  If you use `pip install -e .[dev]`, it will be installed automatically.

- To run the test suite against all supported Python version, run `nox`.
  Our [CI](https://github.com/hynek/doc2dash/actions) runs it the same way.

- To build the docs run `nox -e docs`, to start a local webserver with the docs run `nox -e docs -- serve`.

- Make sure your changes pass our CI.
  You won't get any feedback until it's green unless you ask for it.

- If your change affects end-users, add an entry to the [changelog](https://github.com/hynek/doc2dash/blob/main/CHANGELOG.md).
  Use present tense, semantic newlines, and add link to your pull request.

- Don’t break backwards-compatibility.

- *Always* add tests and docs for your code.
  This is a hard rule; patches with missing tests or documentation won’t be merged.

- Write [good test docstrings](https://jml.io/test-docstrings/).

- Obey [PEP 8](https://peps.python.org/pep-0008/) and [PEP 257](https://peps.python.org/pep-0257/).

- To install a development version of *doc2dash* use `pip install -Ue .[dev]`.
  We recommend using the Python version from `.python-version-default`.

- We also recommend to install [_pre-commit_](https://pre-commit.com) and running `pre-commit install` to prevent unnecessary CI breakage.

Please note that this project is released with a [Contributor Code of Conduct](https://github.com/hynek/doc2dash/blob/main/.github/CODE_OF_CONDUCT.md).
By participating in this project you agree to abide by its terms.
Please report any harm to [Hynek Schlawack](https://hynek.me/about/) in any way you find appropriate.

Thank you for contributing to *doc2dash*!
