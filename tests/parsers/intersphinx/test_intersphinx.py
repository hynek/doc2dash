from __future__ import absolute_import, division, print_function

import os

from doc2dash.parsers.intersphinx import InterSphinxParser, _inv_to_entries


HERE = os.path.dirname(__file__)


class TestInterSphinxParser(object):
    def test_parses(self):
        """
        Parsing does not fail.
        """
        p = InterSphinxParser(os.path.join(HERE))
        for t in p.parse():
            pass

    def test_inv_to_entries(self):
        """
        Inventory items are correctly converted.
        """
        result = list(
            _inv_to_entries({"py:method": {
                "some_method": (None, None, u"some_module.py", u"-"),
            }})
        )
        assert [('some_method', 'Method', 'some_module.py')] == result
