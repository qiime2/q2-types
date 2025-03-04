# ----------------------------------------------------------------------------
# Copyright (c) 2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin.testing import TestPluginBase

from q2_types.kraken2 import (Kraken2ReportDirectoryFormat,
                              Kraken2OutputDirectoryFormat)

from q2_types.kraken2._deferred_setup._partitioners import (
    _partition_kraken2_reports, _partition_kraken2_outputs)


class kraken2PartitionersTests(TestPluginBase):
    package = "q2_types.kraken2.tests"

    def setUp(self):
        super().setUp()

        self.report_reads = Kraken2ReportDirectoryFormat(
            self.get_data_path("reports-reads"), mode="r"
        )
        self.output_reads = Kraken2OutputDirectoryFormat(
            self.get_data_path("outputs-reads"), "r"
        )

    def test_partition_report_by_sample(self):
        num_samples = 2
        partitioned_reports = _partition_kraken2_reports(self.report_reads,
                                                         num_partitions=None)
        self.assertEqual(len(partitioned_reports.items()), num_samples)
        for idx, (id, sample) in enumerate(partitioned_reports.items()):
            print("partitioned report", idx)
            print(id)
            print(sample)

    def test_partition_report_by_specified_n(self):
        num_partitions = 1
        partitioned_reports = _partition_kraken2_reports(self.report_reads,
                                                         num_partitions)
        self.assertEqual(len(partitioned_reports.items()), num_partitions)
        for idx, (id, sample) in enumerate(partitioned_reports.items()):
            print("partitioned report", idx)
            print(id)
            print(sample)

    def test_partition_report_more_than_samples(self):
        num_samples = 2

        with self.assertWarnsRegex(
                UserWarning, "You have requested a number of.*100.*2.*2"):
            partitioned_reports = _partition_kraken2_reports(self.report_reads,
                                                             100)
            self.assertEqual(len(partitioned_reports.items()), num_samples)

    def test_partition_output_by_sample(self):
        num_samples = 2
        partitioned_output = _partition_kraken2_outputs(self.output_reads,
                                                        num_partitions=None)
        self.assertEqual(len(partitioned_output.items()), num_samples)
        for idx, (id, sample) in enumerate(partitioned_output.items()):
            print("partitioned report", idx)
            print(id)
            print(sample)

    def test_partition_output_by_specified_n(self):
        num_partitions = 1
        partitioned_output = _partition_kraken2_outputs(self.output_reads,
                                                        num_partitions)
        self.assertEqual(len(partitioned_output.items()), num_partitions)
        for idx, (id, sample) in enumerate(partitioned_output.items()):
            print("partitioned report", idx)
            print(id)
            print(sample)

    def test_partition_output_more_than_samples(self):
        num_samples = 2
        with self.assertWarnsRegex(
                UserWarning, "You have requested a number of.*100.*2.*2"):
            partitioned_output = _partition_kraken2_reports(self.output_reads,
                                                            100)
            self.assertEqual(len(partitioned_output.items()), num_samples)
