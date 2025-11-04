# Requirements and Installation

## Homebrew 🍻

For [Homebrew](https://brew.sh) users *doc2dash* is available from a [Homebrew tap](https://github.com/hynek/homebrew-tap):

```console
$ brew install hynek/tap/doc2dash
```


## PyPI

The latest stable version can be always found on [PyPI](https://pypi.org/project/doc2dash/).

If you have [*uv* installed](https://docs.astral.sh/uv/getting-started/installation/), running doc2dash is as simple as:

```console
$ uvx run doc2dash --help
```

*uv* will even install Python for you if necessary.
All platforms that run Python are supported.


## Viewer

To view the results, you will need a docset viewer, the most commonly known being [Dash](https://kapeli.com/dash/) for macOS.

Other alternatives have been developed in cooperation with Dash's developer [Kapeli](https://twitter.com/kapeli):

- [*helm-dash*](https://github.com/areina/helm-dash) for Emacs,
- and [Zeal](https://zealdocs.org/) for Linux and Windows.

*doc2dash* is only tested against the original Dash, though.
