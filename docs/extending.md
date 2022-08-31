# Writing Custom Parser Plugins

A *doc2dash* parser plugin has three jobs:

1. Detect whether it can parse a directory and extract a fitting name.
2. Parse a directory and tell *doc2dash* about all entries that it wants indexed.
3. Patch files such that *Dash.app* can [generate per-file tables of contents](https://kapeli.com/docsets#tableofcontents).

For that, it must implement the `Parser` protocol:

## `Parser`

::: doc2dash.parsers.types.Parser
    options:
      members:
        - detect
        - __init__
        - parse
        - find_and_patch_entry


## `ParserEntry`

::: doc2dash.parsers.types.ParserEntry
    options:
      members:
        - name
        - type
        - path

---

To help you, *doc2dash* comes with a few helpers:

## `format_ref`

::: doc2dash.parsers.utils.format_ref

---

To use your custom parser, you have to invoke *doc2dash* with the `--parser` option and specify the importable path to it.


## Examples

Often, it's the easiest to get started by looking at existing parsers.
Conveniently, *doc2dash* ships two:

- The [*intersphinx* parser](https://github.com/hynek/doc2dash/blob/main/src/doc2dash/parsers/intersphinx.py) uses a machine-readable format to extract the necessary metadata.
- The [*pydoctor* parser](https://github.com/hynek/doc2dash/blob/main/src/doc2dash/parsers/pydoctor.py) actually parses the HTML of the pages.
