# Writing Custom Parsers

Adding your own parsers is easy!
We'd prefer if you'd share your parsers with us, but you can always use your own parser.

You have to implement the `doc2dash.parsers.types.IParser` interface which consists of three methods:

- A static method `detect(path: str) -> bool` that takes a path and returns whether of not that path contains documentation is recognizes.
- A static method `guess_name(path: str) -> str | None` that takes a path and returns a guess of the name of the project that *path* is documenting.
  `None` is a valid return value and means "no idea".
- A generator `parse(self) -> Generator[ParserEntry, None, None]` that yields `ParserEntry`s.
- A regular method `find_and_patch_entry(self, soup: BeautifulSoup, entry: TOCEntry) -> bool`.

  It returns whether it found and patched the entry.

To help you, *doc2dash* comes with a few helpers.

Finally, when calling *doc2dash*, you must pass the fully-qualified name using the `--parser` option.

---

Often, it's the easiest to get started by looking at existing parsers.
Conveniently, *doc2dash* ships two:

- The [`intersphinx` parser](https://github.com/hynek/doc2dash/blob/main/src/doc2dash/parsers/intersphinx.py) uses a machine-readable format to extract the necessary metadata.
- The [*pydoctor*](https://github.com/hynek/doc2dash/blob/main/src/doc2dash/parsers/pydoctor.py) parser actually parses the HTML of the pages.
