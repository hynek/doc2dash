# Requirements and Installation

## Homebrew 🍻

For [*Homebrew*](https://brew.sh) users *doc2dash* is available from a [*Homebrew* tap](https://github.com/hynek/homebrew-tap):

```console
$ brew install hynek/tap/doc2dash
```

We try to provide as many pre-built bottles as possible.


## Binaries

As of version 3.0, the [releases](https://github.com/hynek/doc2dash/releases) come with **pre-compiled binaries** for Linux, macOS, and Windows on Intel x64 that you can simply download and run *without* any other dependencies.

> [!WARNING]
> On macOS, you may get a warning about an unsigned binary.
> To get rid of that you have two options:
>
> 1. Run `xattr -d com.apple.quarantine ~/Downloads/doc2dash/doc2dash` after unpacking the downloaded archive inside your Downloads folder.
> 1. Open the binary in Finder once using right-click.


## PyPI

If your platform is not supported yet (or doesn't work), the latest stable version can be always found on [PyPI](https://pypi.org/project/doc2dash/).

A good way to run it without ruining your Python installation is [*pipx*](https://pipxproject.github.io/pipx/).
Either by installing it first, or by running it directly:

```console
$ pipx run doc2dash --help
```

As of version 2.4, *doc2dash* only supports Python 3.8 and later.
If you need to run it on an older Python version, use one of the 2.x releases that are available on [PyPI](https://pypi.org/project/doc2dash/).

All platforms that run Python are supported.


## Viewer

To view the results, you will need a docset viewer, the most commonly known being [Dash](https://kapeli.com/dash/) for macOS.

Other alternatives have been developed in cooperation with Dash's developer [Kapeli](https://twitter.com/kapeli):

- [*helm-dash*](https://github.com/areina/helm-dash) for Emacs,
- and [Zeal](https://zealdocs.org/) for Linux and Windows.

*doc2dash* is only tested against the original Dash, though.
