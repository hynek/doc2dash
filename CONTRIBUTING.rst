How To Contribute
=================

Every open source project lives from the generous help by contributors that sacrifice their time and ``doc2dash`` is no different.

Here are a few guidelines to get you started:

- No contribution is too small; please submit as many fixes for typos and grammar bloopers as you can!
- Try to limit each pull request to one change only.
- To run the test suite, all you need is a recent tox_.
  It will ensure the test suite runs with all dependencies against all Python versions just as it will in our `CI`_.
  If you lack some Python version, you can can always limit the environments like ``tox -e py27,py35`` (in that case you may want to look into pyenv_ that makes it very easy to install many different Python versions in parallel).
- Make sure your changes pass our CI.
  You won't get any feedback until it's green unless you ask for it.
- If your change is noteworthy, add an entry to the changelog_.
  Use present tense, semantic newlines, and add link to your pull request.
- Don’t break backward compatibility.
- *Always* add tests and docs for your code.
  This is a hard rule; patches with missing tests or documentation won’t be merged.
- Write `good test docstrings`_.
- Obey `PEP 8`_ and `PEP 257`_.
- If you address review feedback, make sure to bump the pull request to notify us that you're done.
- To install a development version of ``doc2dash`` use ``pip install -Ue .[dev]``.
  We also recommend to run ``pre-commit install`` to prevent unnecessary CI breakage.

Please note that this project is released with a Contributor `Code of Conduct`_.
By participating in this project you agree to abide by its terms.
Please report any harm to `Hynek Schlawack <https://hynek.me/about/>`_ in any way you find appropriate.

Thank you for considering to contribute to ``doc2dash``!


.. _`PEP 8`: https://www.python.org/dev/peps/pep-0008/
.. _`PEP 257`: https://www.python.org/dev/peps/pep-0257/
.. _`good test docstrings`: https://jml.io/pages/test-docstrings.html
.. _`Code of Conduct`: https://github.com/hynek/doc2dash/blob/master/CODE_OF_CONDUCT.rst
.. _changelog: https://github.com/hynek/doc2dash/blob/master/CHANGELOG.rst
.. _`tox`: https://testrun.org/tox/
.. _`CI`: https://github.com/hynek/doc2dash/actions
.. _pyenv: https://github.com/pyenv/pyenv
