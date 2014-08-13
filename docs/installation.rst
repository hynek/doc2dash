Installation
============

The latest stable version can be always found on PyPI_ and can therefore be installed using a simple::

   $ pip install --user doc2dash

If you haven’t pip_ yet, installation should be as easy as::

   $ curl https://raw.github.com/pypa/pip/master/contrib/get-pip.py | python

``doc2dash`` runs on Python 2.7, and 3.3+, and PyPy.


.. _clones:

Viewer
------

To view the results, you will need a docset viewer, the most commonly known being `Dash.app`_ for OS X.

Other alternatives have been developed in cooperation with Dash.app's developer `Kapeli <https://twitter.com/kapeli>`_:

- `helm-dash <https://github.com/areina/helm-dash>`_ for Emacs,
- `lovelydocs <http://lovelydocs.io/>`_ for Android,
- `velocity <http://velocity.silverlakesoftware.com/>`_ for Windows,
- and `zeal <http://zealdocs.org/>`_ for Linux and Windows.

``doc2dash`` is only tested against the original Dash.app though.


.. _pip: https://pip.pypa.io/en/latest/installing.html#install-pip
.. _PyPI: https://pypi.python.org/pypi/doc2dash/
.. _`Dash.app`: http://kapeli.com/dash/
