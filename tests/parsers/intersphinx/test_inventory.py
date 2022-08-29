from doc2dash.parsers.sphinx_inventory import load_inventory


def test_parse_example(objects_inv):
    """
    Parses our example objects.inv correctly.
    """
    with objects_inv.open("rb") as f:
        entries = dict(load_inventory(f))

    assert {
        "py:attribute": {
            "some_module.LeClass.AnAttr": (
                "index.html#some_module.LeClass.AnAttr",
                "-",
            )
        },
        "py:class": {
            "some_module.LeClass": ("index.html#some_module.LeClass", "-")
        },
        "py:data": {
            "some_module.BoringData": (
                "index.html#some_module.BoringData",
                "-",
            )
        },
        "py:function": {
            "some_module.func": ("index.html#some_module.func", "-")
        },
        "py:method": {
            "some_module.LeClass.DieMethod": (
                "index.html#some_module.LeClass.DieMethod",
                "-",
            )
        },
        "py:module": {"some_module": ("index.html#module-some_module", "-")},
        "py:property": {
            "some_module.LeClass.Mine": (
                "index.html#some_module.LeClass.Mine",
                "-",
            )
        },
        "std:cmdoption": {"--foo": ("index.html#cmdoption-foo", "-")},
        "std:doc": {
            "index": (
                "index.html",
                "Let’s define some symbols and see if doc2dash can handle "
                "them!",
            )
        },
        "std:envvar": {
            "ENV_VARIABLE": ("index.html#envvar-ENV_VARIABLE", "-")
        },
        "std:label": {
            "genindex": ("genindex.html", "Index"),
            "modindex": ("py-modindex.html", "Module Index"),
            "py-modindex": ("py-modindex.html", "Python Module Index"),
            "search": ("search.html", "Search Page"),
        },
        "std:term": {"Foobar": ("index.html#term-Foobar", "-")},
    } == entries
