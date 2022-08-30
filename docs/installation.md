# Requirements and Installation

The latest stable version can be always found on [PyPI](https://pypi.org/project/doc2dash/).

A good way to run it without ruining your Python installation is [*pipx*](https://pipxproject.github.io/pipx/).
Either by installing it first, or just by running it directly:

```shell
$ pipx run doc2dash --help
```

As of version 2.4, *doc2dash* only supports Python 3.8 and later.
If you need to run it on an older Python version, use one of the 2.x releases that are available on [PyPI](https://pypi.org/project/doc2dash/).

All platforms that run Python are supported.
*doc2dash* comes with a few *Dash.app*-specific features that naturally only work on macOS.


## Viewer

To view the results, you will need a docset viewer, the most commonly known being [*Dash.app*](https://kapeli.com/dash/) for macOS.

Other alternatives have been developed in cooperation with *Dash.app*'s developer [Kapeli](https://twitter.com/kapeli):

- [*helm-dash*](https://github.com/areina/helm-dash) for Emacs,
- and [*zeal*](https://zealdocs.org/) for Linux and Windows.

*doc2dash* is only tested against the original *Dash.app* though.
