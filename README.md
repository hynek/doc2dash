# Create Docsets for Dash.app and Friends

[![Documentation](https://img.shields.io/badge/Docs-Read%20The%20Docs-black)](https://doc2dash.readthedocs.io/)
[![License: MIT](https://img.shields.io/badge/license-MIT-C06524)](https://github.com/hynek/doc2dash/blob/main/LICENSE)
[![Current PyPI release](https://img.shields.io/pypi/v/doc2dash)](https://pypi.org/project/doc2dash/)
[![Downloads per month](https://static.pepy.tech/personalized-badge/doc2dash?period=month&units=international_system&left_color=grey&right_color=blue&left_text=Downloads%20/%20Month)](https://pepy.tech/project/doc2dash)

<!-- begin-short -->

*doc2dash* is an extensible [Documentation Set](https://developer.apple.com/library/archive/documentation/DeveloperTools/Conceptual/Documentation_Sets/010-Overview_of_Documentation_Sets/docset_overview.html#//apple_ref/doc/uid/TP40005266-CH13-SW6) (*docset*) generator that helps you to have documentation for all your favorite APIs in [*Dash.app*-compatible](https://kapeli.com/dash/) API browsers.

An API browser is an application that runs locally on your computer and allows you to search various API docs by pressing a key combination and starting to type (I have bound it to Alt-Space bar and can't write code without it).

The most common ones – [*Dash.app*](https://kapeli.com/dash) (macOS) and [*Zeal*](https://zealdocs.org) (Windows and Linux) – come with **many** docsets out of the box, but they can never offer you docsets for *every* package you'll ever use.
This is where *doc2dash* comes in:
It takes your offline documentation and converts it into an indexed format that API browsers can read and search (very fast!).

Currently it supports:

- *intersphinx*-based documentation like [*Sphinx*](https://www.sphinx-doc.org/) or [*MkDocs*](https://www.mkdocs.org) (with [*mkdocstrings*](https://mkdocstrings.github.io))
- [*pydoctor*](https://github.com/twisted/pydoctor)

It's also fully extendable: **you** can write your own private parser!

![doc2dash Session](docs/doc2dash-session.png)


## Project Information

- **License**: [MIT](https://github.com/hynek/doc2dash/blob/main/LICENSE)
- **PyPI**: <https://pypi.org/project/doc2dash/>
- **Source Code**: <https://github.com/hynek/doc2dash>
- **Documentation**: <https://doc2dash.readthedocs.io/>
- **Changelog**: <https://github.com/hynek/doc2dash/blob/main/CHANGELOG.md>
- **Supported Python Versions**: 3.8 and later (check the changelog for past releases that support _much_ older Python versions)
- **Platforms**: Both Linux and macOS are tested; Windows should work too.
