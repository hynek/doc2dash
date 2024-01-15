# Building and Submitting Docsets to Dash.app

> [!NOTE]
> This how-to is extracted from [*How I'm a Productive Programmer With a Memory of a Fruit Fly*](https://hynek.me/articles/productive-fruit-fly-programmer/).

The goal of this how-to is to teach you how to convert *intersphinx*-compatible documentation to a docset and how to submit it to Dash's [*user-generated docset registry*](https://github.com/Kapeli/Dash-User-Contributions), such that others don't have to duplicate your work.

I'll assume you have picked and installed your API browser of choice.
It doesn't matter which one you use, but this how-to guide uses Dash.
For *optionally* submitting the docset at the end, you'll also need a basic understanding of GitHub and its [pull request workflow](https://docs.github.com/en/get-started/quickstart/contributing-to-projects).

**I** will be using this how-to as an occasion to *finally* start publishing docsets of my own projects, starting with [*structlog*](https://www.structlog.org/).
I suggest **you** pick an *intersphinx*-compatible project that isn't supported by Dash yet and whose documentation's tab you visit most often.


## Building Documentation

We start with the biggest problem and source of frequent feature requests for *doc2dash*:
you need the documentation in a complete, built form.
Usually, that means that you have to download the repository and figure out how to build the docs before even installing *doc2dash* because most documentation sites unfortunately don't offer a download of the whole thing.

My heuristic is to look for a `tox.ini` or `noxfile.py` first and see if it builds the documentation.
If it doesn't, I look for a [`.readthedocs.yaml`](https://dev.readthedocs.io/en/latest/design/yaml-file.html), and if even that lets me down, I'm on the lookout for files named like `docs-requirements.txt` or optional installation targets like `docs`.
My final hope is to go through pages of YAML and inspect CI configurations.

Once you've managed to install all dependencies, it's usually just a matter of `make html` in the documentation directory.

---

After figuring this out, you should have a directory called `_build/html` for Sphinx or `site` for MkDocs.

> [!NOTE]
> Please note with MkDocs that if the project doesn't use the [*mkdocstrings*](https://mkdocstrings.github.io) extension -- which, alas, is virtually all of the popular ones at the moment -- there won't be an `objects.inv` file and therefore no API data to be consumed.
>
> I hope that more MkDocs-based projects add support for *mkdocstrings* in the future!
> As with Sphinx, it's language-agnostic.


## Converting

Following the hardest step comes the easiest one:
converting the documentation we've just built into a docset.

All you have to do is point *doc2dash* at the directory with HTML documentation and wait:

```console
$ doc2dash _build/html
```

That's all!

*doc2dash* knows how to extract the name from the *intersphinx* index and uses it by default (you can override it with `--name`).
You should be able to add this docset to an API browser of your choice and everything should work.

---

If you pass `--add-to-dash` or `-a`, the final docset is automatically added to Dash when it's done.
If you pass `--add-to-global` or `-A`, it moves the finished docset to a global directory (`~/Library/Application Support/doc2dash/DocSets`) and adds it from there.
I rarely run *doc2dash* without `-A` when creating docsets for myself.


## Improving Your Documentation Set

Dash's documentation has a [bunch of recommendations](https://kapeli.com/docsets#contributetodash) on how you can improve the docset that we built in the previous step.
It's important to note that the next five steps are strictly optional and more often than not, I skip them because I'm lazy.

But in this case, I want to submit the docset to Dash's user-contributed registry, so let's go the full distance!


### Set the Main Page

With Dash, you can always search *all* installed docsets, but sometimes you want to limit the scope of search.
For example, when I type `p:` (the colon is significant), Dash switches to only searching the latest Python docset.
Before you start typing, it offers you a menu underneath the search box whose first item is "Main Page".

When converting *structlog* docs, this main page is the index that can be useful, but usually not what I want.
When I got to the main page, I want to browse the narrative documentation.

The *doc2dash* option to set the main page is `--index-page` or `-I` and takes the file name of the page you want to use, relative to the documentation root.

Confusingly, the file name of the index is `genindex.html` and the file name of the main page is the HTML-typical `index.html`.
Therefore, we'll add `--index-page index.html` to the command line.


### Add Icons

Documentation sets can have icons that are shown throughout Dash next to the docsets's names and symbols.
That's pretty, but also helpful to recognize where a symbol is coming from when searching across multiple docsets

*structlog* has a cool beaver logo, so let's use [ImageMagick](https://imagemagick.org/) to resize the logo to 16x16 and 32x32 pixels:

```console
$ magick \
    docs/_static/structlog_logo_transparent.png \
    -resize 16x16 \
    docs/_static/docset-icon.png
$ magick \
    docs/_static/structlog_logo_transparent.png \
    -resize 32x32 \
    docs/_static/docset-icon@2x.png
```

Now we can add it to the docset using the `--icon` and `--icon-2x` options.


### Support Online Redirection

Offline docs are awesome, but sometimes it can be useful to jump to the online version of the documentation page you're reading right now.
A common reason is to peruse a newer or older version.

Dash has the menu item "Open Online Page ⇧⌘B" for that, but it needs to know the base URL of the documentation.
You can set that using `--online-redirect-url` or `-u`.

For Python packages on [Read the Docs](https://readthedocs.org) you can pick between the `stable` (last VCS tag) or `latest` (current main branch).

I think `latest` makes more sense, if you leave the comfort of offline documentation, thus I'll add:

```plaintext
--online-redirect-url https://www.structlog.org/en/latest/
```


### Putting It All Together

We're done!
Let's run the whole command line and see how it looks in Dash:

```console
$ doc2dash \
    --index-page index.html \
    --icon docs/_static/docset-icon.png \
    --icon-2x docs/_static/docset-icon@2x.png \
    --online-redirect-url https://www.structlog.org/en/latest/ \
    docs/_build/html
Converting intersphinx docs from '/Users/hynek/FOSS/structlog/docs/_build/html' to 'structlog.docset'.
Parsing documentation...
Added 238 index entries.
Patching for TOCs... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00
```

That's it -- we've got a great docset!


## Automation

Since I want to create a new version of the docsets for every new release, the creation needs to be automated.
*structlog* is already using GitHub Actions as CI, so it makes sense to use it for building the docset too.

For local testing, I'll take advantage of *doc2dash* being a Python project and use a [*tox*](https://tox.wiki/) environment that reuses the dependencies that I use when testing documentation itself.

> [!NOTE]
> *tox* is a combination of Make and a virtual environment manager based on the `ini` file format.
> Its original purpose was testing Python software over multiple Python versions but has grown a lot more powerful.
>
> The big upsides over a `Makefile` are that it's more portable and has support for Python packaging built-in (which is necessary for building the documentation anyways).

The environment installs `structlog[docs]` -- meaning: the package with optional `docs` dependencies, plus *doc2dash*.
Then it runs `commands` in order:

```ini
[testenv:docset]
extras = docs
deps = doc2dash
allowlist_externals =
    rm
    cp
    tar
commands =
    rm -rf structlog.docset docs/_build
    sphinx-build -n -T -W -b html -d {envtmpdir}/doctrees docs docs/_build/html
    doc2dash --index-page index.html --icon docs/_static/docset-icon.png --icon-2x docs/_static/docset-icon@2x.png --online-redirect-url https://www.structlog.org/en/latest/ docs/_build/html
    tar --exclude='.DS_Store' -cvzf structlog.tgz structlog.docset
```

Now I can build a docset just by calling `tox run -e docset`.

Doing that in CI is trivial, but entails tons of boilerplate, so I'll just [link to the workflow](https://github.com/hynek/structlog/blob/main/.github/workflows/build-docset.yml).
Note the `upload-artifact` action at the end that allows me to download the built docsets from the run summaries.

---

At this point, we have a *great* docset that's built *automatically*.
Time to share it with the world!


## Submitting

In the final step, we'll submit our docset to Dash's user-contributed repository, so other people can download it comfortably from Dash's GUI.
Conveniently, Dash uses a concept for the [whole process](https://github.com/Kapeli/Dash-User-Contributions#contribute-a-new-docset) that's probably familiar to every open-source aficionado[^practice]:
GitHub pull requests.

[^practice]: If not: this is a *great* opportunity to practice in a low-stakes environment.

The first step is checking the [*Docset Contribution Checklist*](https://github.com/Kapeli/Dash-User-Contributions/wiki/Docset-Contribution-Checklist). Fortunately we -- or in some cases: *doc2dash* -- have already taken care of everything!

So let's move right along, and fork the <https://github.com/Kapeli/Dash-User-Contributions> repo and clone it to your computer.

First, you have to copy the `Sample_Docset` directory into `docsets` and rename it while doing so.
Thus, the command line is for me:

```console
$ cp -a Sample_Docset docsets/structlog
```

Let's enter the directory with `cd docsets/structlog` and take it from there further.

The main step is adding the docset itself -- but as a *gzipped* Tar file.
The contribution guide even gives us the template for creating it.
In my case the command line is:

```console
$ tar --exclude='.DS_Store' -cvzf structlog.tgz structlog.docset
```

You may have noticed that I've already done the Tar-ing in my *tox* file, so I just have to copy it over:

```console
$ cp ~/FOSS/structlog/structlog.tgz .
```

It also wants the icons *additionally* to what is in the docset, so I copy them from the docset:

```console
$ cp ~/FOSS/structlog/structlog.docset/icon* .
```

Next, it would like us to fill in metadata in the `docset.html` file which is straightforward in my case:

```json
{
    "name": "structlog",
    "version": "24.1.0",
    "archive": "structlog.tgz",
    "author": {
        "name": "Hynek Schlawack",
        "link": "https://github.com/hynek"
    },
    "aliases": []
}
```

Finally, it wants us to write some documentation about who we are and how to build the docset.
After looking at other [examples](https://github.com/Kapeli/Dash-User-Contributions/tree/master/docsets), I've settled on the following:

```markdown
# structlog

<https://www.structlog.org/>

Maintained by [Hynek Schlawack](https://github.com/hynek/).


## Building the Docset

### Requirements

- Python 3.12
- [*tox*](https://tox.wiki/)


### Building

1. Clone the [*structlog* repository](https://github.com/hynek/structlog).
2. Check out the tag you want to build.
3. `tox run -e docset` will build the documentation and convert it into `structlog.docset` in one step.
```

The *tox* trick is paying off -- I don't have to explain Python packaging to anyone!

Don't forget to delete stuff from the sample docset that we don't use:

```console
$ rm -r versions Sample_Docset.tgz
```

---

We're done! Let's check in our changes:

```console
$ git checkout -b structlog
$ git add docsets/structlog
$ git commit -m "Add structlog docset"
[structlog 33478f9] Add structlog docset
 5 files changed, 30 insertions(+)
 create mode 100644 docsets/structlog/README.md
 create mode 100644 docsets/structlog/docset.json
 create mode 100644 docsets/structlog/icon.png
 create mode 100644 docsets/structlog/icon@2x.png
 create mode 100644 docsets/structlog/structlog.tgz
$ git push -u
```

Looking good -- time for a [pull request](https://github.com/Kapeli/Dash-User-Contributions/pull/3891)!

A few hours later: big success!
Everyone can download the *structlog* *Documentation Set* now!
