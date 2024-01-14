# SPDX-FileCopyrightText: 2012 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

import logging

import pytest

from doc2dash.output import create_log_config


class TestSetupLogging:
    @pytest.mark.parametrize(
        "verbose, quiet, expected",
        [
            (False, False, logging.INFO),
            (True, False, logging.DEBUG),
            (False, True, logging.ERROR),
        ],
    )
    def test_logging(self, verbose, quiet, expected):
        """
        Ensure verbosity options cause the correct log level.
        """
        level = create_log_config(verbose, quiet)["loggers"]["doc2dash"][
            "level"
        ]
        assert level is expected
