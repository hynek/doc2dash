from pathlib import Path
from unittest.mock import MagicMock

import pytest

import doc2dash

from doc2dash.parsers import DOCTYPES


@pytest.fixture(name="dt", params=DOCTYPES)
def _dt(request):
    return request.param


def test_get_doctype(monkeypatch):
    monkeypatch.setattr(doc2dash.parsers, "DOCTYPES", [])

    assert doc2dash.parsers.get_doctype("foo") is None

    dt = MagicMock("testtype", detect=lambda _: True)
    monkeypatch.setattr(doc2dash.parsers, "DOCTYPES", [dt])

    assert doc2dash.parsers.get_doctype("foo") is dt


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
