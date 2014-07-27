from __future__ import absolute_import, division, print_function

import os

from doc2dash.parsers.intersphinx import InterSphinxParser


HERE = os.path.dirname(__file__)


class TestInterSphinxParser(object):
    def test_parses(self):
        """
        Parsing does not fail.
        """
        p = InterSphinxParser(os.path.join(HERE))
        for t in p.parse():
            pass
