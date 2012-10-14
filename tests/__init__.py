## -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import shutil
import sys
import tempfile

from contextlib import contextmanager


if sys.version_info.major == 2:

    @contextmanager
    def _TemporaryDirectory():
        name = tempfile.mkdtemp()
        yield name
        shutil.rmtree(name)

    tempfile.TemporaryDirectory = _TemporaryDirectory
