# Usage

Basic usage is as simple as:

    $ doc2dash -A DOCS_DIR

*doc2dash* will create a new directory called `DOCS_DIR.docset` in `~/Library/Application Support/doc2dash/DocSets` containing a Dash-compatible docset. When finished, the docset is automatically added to Dash.


## Environment Variables

*doc2dash* respects [`NO_COLOR`](https://no-color.org).


::: mkdocs-click
    :module: doc2dash.__main__
    :command: main
    :prog_name: doc2dash
    :style: table
    :depth: 1

Refer to our [how-to](how-to.md) and the official [*Docset Generation Guide*](https://kapeli.com/docsets) to learn what those options are good for.
