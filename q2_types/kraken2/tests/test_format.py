# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import os
import unittest

from qiime2.core.exceptions import ValidationError
from qiime2.plugin.testing import TestPluginBase

from q2_types.kraken2._format import (
    Kraken2ReportFormat, Kraken2ReportDirectoryFormat,
    Kraken2OutputFormat, Kraken2OutputDirectoryFormat,
    Kraken2DBReportFormat, Kraken2DBReportDirectoryFormat,
    Kraken2DBDirectoryFormat, BrackenDBDirectoryFormat
)


class TestFormats(TestPluginBase):
    package = 'q2_types.kraken2.tests'

    def test_report_format_ok(self):
        report_fp = self.get_data_path('reports-single/report-ok.txt')
        fmt = Kraken2ReportFormat(report_fp, mode='r')
        fmt.validate()

    def test_db_report_format_ok(self):
        report_fp = self.get_data_path(
            os.path.join('db-reports', 'report.txt')
        )
        fmt = Kraken2DBReportFormat(report_fp, mode='r')
        fmt.validate()

    def test_report_format_missing_col(self):
        report_fp = self.get_data_path(
            'reports-single/report-missing-column.txt'
        )
        fmt = Kraken2ReportFormat(report_fp, mode='r')

        with self.assertRaisesRegex(
            ValidationError, 'found 5'
        ):
            fmt.validate()

    def test_db_report_format_missing_col(self):
        report_fp = self.get_data_path(
            os.path.join('db-reports', 'report-missing-column.txt')
        )
        fmt = Kraken2DBReportFormat(report_fp, mode='r')

        with self.assertRaisesRegex(
            ValidationError, 'found 5'
        ):
            fmt.validate()

    def test_report_format_wrong_types(self):
        report_fp = self.get_data_path(
            'reports-single/report-wrong-types.txt'
        )
        fmt = Kraken2ReportFormat(report_fp, mode='r')

        with self.assertRaisesRegex(
            ValidationError,
                'Expected <class \'float\'> type in the '
                '"perc_frags_covered" column, got int64'
        ):
            fmt.validate()

    def test_db_report_format_wrong_types(self):
        report_fp = self.get_data_path(
            os.path.join('db-reports', 'report-wrong-types.txt')
        )
        fmt = Kraken2DBReportFormat(report_fp, mode='r')

        with self.assertRaisesRegex(
            ValidationError,
                'Expected <class \'float\'> type in the '
                '"perc_minimizers_covered" column, got int64'
        ):
            fmt.validate()

    def test_report_dirfmt_from_reads(self):
        dirpath = self.get_data_path('reports-reads')
        fmt = Kraken2ReportDirectoryFormat(dirpath, mode='r')
        fmt.validate()

    def test_report_dirfmt_from_mags(self):
        dirpath = self.get_data_path('reports-mags')
        fmt = Kraken2ReportDirectoryFormat(dirpath, mode='r')
        fmt.validate()

    def test_db_report_dirfmt(self):
        dirpath = self.get_data_path(
            os.path.join('db-reports', 'report-dir')
        )
        fmt = Kraken2DBReportDirectoryFormat(dirpath, mode='r')
        fmt.validate()

    def test_output_format_ok(self):
        output_fp = self.get_data_path('outputs-single/output-ok.txt')
        fmt = Kraken2OutputFormat(output_fp, mode='r')
        fmt.validate()

    def test_output_format_missing_col(self):
        output_fp = self.get_data_path(
            'outputs-single/output-missing-column.txt'
        )
        fmt = Kraken2OutputFormat(output_fp, mode='r')

        with self.assertRaisesRegex(
            ValidationError, '4 were found'
        ):
            fmt.validate()

    def test_output_format_wrong_first_col(self):
        output_fp = self.get_data_path(
            'outputs-single/output-wrong-first-col.txt'
        )
        fmt = Kraken2OutputFormat(output_fp, mode='r')

        with self.assertRaisesRegex(
            ValidationError, 'Expected the first column to contain only'
        ):
            fmt.validate()

    def test_output_format_only_classified(self):
        output_fp = self.get_data_path(
            'outputs-single/output-only-classified.txt'
        )
        fmt = Kraken2OutputFormat(output_fp, mode='r')
        fmt.validate()

    def test_output_dirfmt_from_reads(self):
        dirpath = self.get_data_path('outputs-reads')
        format = Kraken2OutputDirectoryFormat(dirpath, mode='r')
        format.validate()

    def test_output_dirfmt_from_mags(self):
        dirpath = self.get_data_path('outputs-mags')
        format = Kraken2OutputDirectoryFormat(dirpath, mode='r')
        format.validate()

    def test_kraken2db_dirfmt(self):
        dirpath = self.get_data_path('kraken2-db')
        format = Kraken2DBDirectoryFormat(dirpath, mode='r')
        format.validate()

    def test_brackendb_dirfmt(self):
        dirpath = self.get_data_path('bracken-db')
        format = BrackenDBDirectoryFormat(dirpath, mode='r')
        format.validate()


if __name__ == '__main__':
    unittest.main()
