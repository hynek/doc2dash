# Usage

Basic usage is as simple as:

    $ doc2dash -A DOCS_DIR

*doc2dash* will create a new directory called `DOCS_DIR.docset` in `~/Library/Application Support/doc2dash/DocSets` containing a *Dash.app*-compatible docset. When finished, the docset is automatically added to *Dash.app*.

::: mkdocs-click
    :module: doc2dash.__main__
    :command: main
    :prog_name: doc2dash
    :style: table
    :depth: 1
