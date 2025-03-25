# ----------------------------------------------------------------------------
# Copyright (c) 2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import pandas as pd

from qiime2.plugin.testing import TestPluginBase

from q2_types.kraken2 import (Kraken2ReportDirectoryFormat,
                              Kraken2OutputDirectoryFormat,
                              Kraken2ReportFormat, Kraken2OutputFormat,
                              )

from q2_types.kraken2._partitioners import _partition_kraken2_results


class Kraken2PartitionersTests(TestPluginBase):
    package = "q2_types.kraken2.tests"

    def setUp(self):
        super().setUp()

        self.report_reads = Kraken2ReportDirectoryFormat(
            self.get_data_path("reports-reads"), mode="r"
        )
        self.output_reads = Kraken2OutputDirectoryFormat(
            self.get_data_path("outputs-reads"), "r"
        )

    def _partition_result_by_sample(self, directoryfmt):
        if isinstance(directoryfmt, Kraken2ReportDirectoryFormat):
            result_format = Kraken2ReportFormat
        elif isinstance(directoryfmt, Kraken2OutputDirectoryFormat):
            result_format = Kraken2OutputFormat

        num_samples = 2
        partitioned_reports = _partition_kraken2_results(
            directoryfmt, num_partitions=None
        )
        exp_dict = directoryfmt.file_dict()

        self.assertEqual(len(partitioned_reports), num_samples)
        for idx, (id, sample) in enumerate(partitioned_reports.items()):
            exp_df = result_format(
                exp_dict[id], mode="r"
            ).view(pd.DataFrame)

            obs_dict = sample.file_dict()
            self.assertEqual(len(obs_dict), 1)
            obs_df = result_format(
                obs_dict[id], mode="r"
            ).view(pd.DataFrame)

            pd.testing.assert_frame_equal(obs_df, exp_df)

    def _partition_result_by_specified_n(self, directoryfmt):
        if isinstance(directoryfmt, Kraken2ReportDirectoryFormat):
            result_format = Kraken2ReportFormat
        elif isinstance(directoryfmt, Kraken2OutputDirectoryFormat):
            result_format = Kraken2OutputFormat

        num_partitions = 1
        partitioned_reports = _partition_kraken2_results(
            directoryfmt, num_partitions
        )
        exp_dict = directoryfmt.file_dict()
        self.assertEqual(len(partitioned_reports), num_partitions)
        for idx, (id, sample) in enumerate(partitioned_reports.items()):
            # iterate through samples in Kraken2 partition
            for exp_key in exp_dict:

                exp_df = result_format(
                    exp_dict[exp_key], mode="r"
                ).view(pd.DataFrame)

                obs_dict = sample.file_dict()
                self.assertEqual(len(obs_dict), 2)
                obs_df = result_format(
                    obs_dict[exp_key], mode="r"
                ).view(pd.DataFrame)

                pd.testing.assert_frame_equal(obs_df, exp_df)

    def _partition_result_more_than_samples(self, directoryfmt):
        if isinstance(directoryfmt, Kraken2ReportDirectoryFormat):
            result_format = Kraken2ReportFormat
        elif isinstance(directoryfmt, Kraken2OutputDirectoryFormat):
            result_format = Kraken2OutputFormat

        num_samples = 2

        exp_dict = directoryfmt.file_dict()

        with self.assertWarnsRegex(
                UserWarning, "You have requested a number of.*100.*2.*2"):
            partitioned_reports = _partition_kraken2_results(directoryfmt, 100)
            self.assertEqual(len(partitioned_reports), num_samples)
            for idx, (id, sample) in enumerate(partitioned_reports.items()):
                exp_df = result_format(
                    exp_dict[id], mode="r"
                ).view(pd.DataFrame)

                obs_dict = sample.file_dict()
                self.assertEqual(len(obs_dict), 1)
                obs_df = result_format(
                    obs_dict[id], mode="r"
                ).view(pd.DataFrame)

                pd.testing.assert_frame_equal(obs_df, exp_df)

    def test_output_partitions(self):
        self._partition_result_by_sample(self.output_reads)
        self._partition_result_by_specified_n(self.output_reads)
        self._partition_result_more_than_samples(self.output_reads)

    def test_report_partitions(self):
        self._partition_result_by_sample(self.report_reads)
        self._partition_result_by_specified_n(self.report_reads)
        self._partition_result_more_than_samples(self.report_reads)
