# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import os
import unittest

import pandas as pd
from pandas._testing import assert_frame_equal
from qiime2.plugin.testing import TestPluginBase

from q2_types.kraken2 import (
    Kraken2ReportFormat, Kraken2OutputFormat, Kraken2DBReportFormat
)


class TestTransformers(TestPluginBase):
    package = "q2_types.kraken2.tests"

    def setUp(self):
        super().setUp()

    def apply_transformation(self, from_fmt, to_fmt, datafile_fp):
        transformer = self.get_transformer(from_fmt, to_fmt)
        fp = self.get_data_path(datafile_fp)
        return transformer(from_fmt(fp, 'r'))

    def test_kraken2_report_to_df(self):
        obs = self.apply_transformation(
            Kraken2ReportFormat,
            pd.DataFrame,
            'reports-single/report-ok.txt'
        )
        exp = pd.read_csv(self.get_data_path('report-ok-table.csv'))
        assert_frame_equal(exp, obs)

    def test_kraken2_output_to_df(self):
        obs = self.apply_transformation(
            Kraken2OutputFormat,
            pd.DataFrame,
            'outputs-contigs/output-ok.txt'
        )
        exp = pd.read_csv(self.get_data_path(
            os.path.join('outputs-contigs', 'output-ok-table.csv'))
        )
        assert_frame_equal(exp, obs)

    def test_kraken2_db_report_to_df(self):
        obs = self.apply_transformation(
            Kraken2DBReportFormat,
            pd.DataFrame,
            os.path.join('db-reports', 'report.txt')
        )
        exp = pd.read_csv(self.get_data_path(
            os.path.join('db-reports', 'report-ok.csv'))
        )
        assert_frame_equal(exp, obs)


if __name__ == '__main__':
    unittest.main()
