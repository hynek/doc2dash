# SPDX-FileCopyrightText: 2012 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

from pathlib import Path
from unittest.mock import Mock

import pytest

import doc2dash

from doc2dash.parsers import DOCTYPES


@pytest.fixture(name="dt", params=DOCTYPES)
def _dt(request):
    return request.param


def test_get_doctype_no_match(tmp_path):
    """
    If nothing matches, return (None, None).
    """
    assert (None, None) == doc2dash.parsers.get_doctype(tmp_path)


def test_get_doctype_first_match(monkeypatch):
    """
    A matching parser's name gets returned.
    """
    dt = Mock("testtype", detect=lambda _: "foo")

    monkeypatch.setattr(doc2dash.parsers, "DOCTYPES", [dt])

    assert (dt, "foo") == doc2dash.parsers.get_doctype("foo")


class TestDetectors:
    @pytest.mark.skipif(
        not Path("test_data").exists(), reason="No test_data present."
    )
    def test_detectors_detect(self, dt):
        """
        Everything that is inside `test_data` is detected by respective
        parsers.
        """
        type_dir = Path("test_data") / dt.name
        for d in type_dir.glob("*"):
            assert dt.detect(d)

    def test_detect_handles_enoent_gracefully(self, dt):
        """
        Non-existent paths are treated like they don't belong to the parser.
        """
        for dt in DOCTYPES:
            assert not dt.detect(Path("foo"))


def raiser(exc):
    def _raiser(*args, **kwargs):
        raise exc()

    return _raiser
