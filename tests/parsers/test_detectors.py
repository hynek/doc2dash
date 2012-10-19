import os

import pytest
from mock import MagicMock

import doc2dash
from doc2dash.parsers import DOCTYPES


def test_get_doctype(monkeypatch):
    monkeypatch.setattr(doc2dash.parsers, 'DOCTYPES', [])
    assert doc2dash.parsers.get_doctype('foo') is None
    dt = MagicMock('testtype', detect=lambda _: True)
    monkeypatch.setattr(doc2dash.parsers, 'DOCTYPES', [dt])
    assert doc2dash.parsers.get_doctype('foo') is dt


if not os.path.exists('test_data'):
    print('Skipping detector tests since no test_data is present.')
else:
    def test_detectors_detect_no_false_positives():
        for dt in DOCTYPES:
            others = set(os.listdir('test_data')) - {dt.name}
            for t in others:
                type_path = os.path.join('test_data', t)
                for d in os.listdir(type_path):
                    assert not dt.detect(os.path.join(type_path, d))

    def test_detectors_detect():
        for dt in DOCTYPES:
            type_dir = os.path.join('test_data', dt.name)
            for d in os.listdir(type_dir):
                assert dt.detect(os.path.join(type_dir, d))


def test_detect_reraises_everything_except_enoent(monkeypatch):
    def raiser(exc):
        def _raiser(*args, **kwargs):
            raise exc()
        return _raiser

    for dt in DOCTYPES:
        for exc in IOError, ValueError:
            with pytest.raises(exc):
                monkeypatch.setattr(os.path, 'join', raiser(exc))
                dt.detect('foo')


def test_detect_handles_enoent_gracefully():
    for dt in DOCTYPES:
        assert not dt.detect('foo')
