Requirements and Installation
=============================

The latest stable version can be always found on PyPI_.

.. warning::

   Since ``doc2dash`` is an application, it has hard-coded dependency versions.
   I strongly discourage from installing it into your global ``site-packages`` because it will inevitably lead to conflicts_.
   Either use pipsi_ or create a virtualenv_ by hand.


``doc2dash`` runs on Python 2.7, and 3.4+, and PyPy.
Both Linux and macOS are supported although certain features are only available on macOS.

.. note::

   For best performance when converting large pieces documentation, I *strongly* recommend using PyPy as the interpreter of choice.


.. _clones:

Viewer
------

To view the results, you will need a docset viewer, the most commonly known being `Dash.app`_ for macOS.

Other alternatives have been developed in cooperation with Dash.app's developer `Kapeli <https://twitter.com/kapeli>`_:

- `helm-dash <https://github.com/areina/helm-dash>`_ for Emacs,
- `velocity <http://velocity.silverlakesoftware.com/>`_ for Windows,
- and `zeal <https://zealdocs.org/>`_ for Linux and Windows.

``doc2dash`` is only tested against the original Dash.app though.


.. _pip: https://pip.pypa.io/en/latest/installing.html
.. _PyPI: https://pypi.org/project/doc2dash/
.. _`Dash.app`: https://kapeli.com/dash/
.. _pipsi: https://github.com/mitsuhiko/pipsi
.. _virtualenv: https://virtualenv.readthedocs.io/
.. _conflicts: https://hynek.me/articles/virtualenv-lives/
