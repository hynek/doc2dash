# Writing Custom Parsers

If you want to implement your own parser (and if you do: why don't you [share it with us](https://github.com/hynek/doc2dash/pulls)? :pleading_face:) you have to implement the [`IParser`][doc2dash.parsers.types.IParser] interface:


## IParser

::: doc2dash.parsers.types.IParser
    options:
      members:
        - detect
        - guess_name
        - parse
        - find_and_patch_entry


## ParserEntry

::: doc2dash.parsers.types.ParserEntry
    options:
      members:
        - name
        - type
        - path

---

To help you, *doc2dash* comes with a few helpers.

Finally, when calling *doc2dash*, you must pass the fully-qualified name using the `--parser` option.


## Examples

Often, it's the easiest to get started by looking at existing parsers.
Conveniently, *doc2dash* ships two:

- The [*intersphinx* parser](https://github.com/hynek/doc2dash/blob/main/src/doc2dash/parsers/intersphinx.py) uses a machine-readable format to extract the necessary metadata.
- The [*pydoctor* parser](https://github.com/hynek/doc2dash/blob/main/src/doc2dash/parsers/pydoctor.py) actually parses the HTML of the pages.
