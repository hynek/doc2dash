# Writing Custom Parser Plugins

A *doc2dash* parser plugin has three jobs:

1. Detect whether it can parse a directory and extract an appropriate name for the *docset*.
2. Parse a directory and tell *doc2dash* about all entries that should be indexed.
3. Patch files such that Dash can [generate per-file tables of contents](https://kapeli.com/docsets#tableofcontents).

For that, it must implement the `Parser` protocol:

## `Parser`

::: doc2dash.parsers.types.Parser
    options:
      members:
        - detect
        - __init__
        - parse
        - make_patcher_for_file


## `Patcher`

::: doc2dash.parsers.types.Patcher


## `ParserEntry`

::: doc2dash.parsers.types.ParserEntry
    options:
      members:
        - name
        - type
        - path


## `EntryType`

::: doc2dash.parsers.types.EntryType


---

To use your custom parser, you have to invoke *doc2dash* with the `--parser` option and specify the importable path to it.


## Example

Often, it's the easiest to get started by looking at existing parsers.
Conveniently, *doc2dash* ships one:

The [*intersphinx* parser](https://github.com/hynek/doc2dash/blob/main/src/doc2dash/parsers/intersphinx.py) uses a machine-readable format to extract the necessary metadata.
