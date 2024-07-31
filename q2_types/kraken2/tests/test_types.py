# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest

from q2_types.feature_data import FeatureData
from q2_types.sample_data import SampleData
from qiime2.plugin.testing import TestPluginBase

from q2_types.kraken2 import (
    Kraken2ReportDirectoryFormat, Kraken2OutputDirectoryFormat,
    Kraken2DBDirectoryFormat, Kraken2DBReportDirectoryFormat,
    BrackenDBDirectoryFormat
)
from q2_types.kraken2 import (
    Kraken2Reports, Kraken2Outputs, Kraken2DB, Kraken2DBReport, BrackenDB
)


class TestTypes(TestPluginBase):
    package = "q2_types.kraken2.tests"

    def test_reports_semantic_type_registration(self):
        self.assertRegisteredSemanticType(Kraken2Reports)

    def test_reports_semantic_type_to_format_registration_sd(self):
        self.assertSemanticTypeRegisteredToFormat(
            SampleData[Kraken2Reports],
            Kraken2ReportDirectoryFormat
        )

    def test_reports_semantic_type_to_format_registration_fd(self):
        self.assertSemanticTypeRegisteredToFormat(
            FeatureData[Kraken2Reports],
            Kraken2ReportDirectoryFormat
        )

    def test_outputs_semantic_type_registration(self):
        self.assertRegisteredSemanticType(Kraken2Outputs)

    def test_outputs_semantic_type_to_format_registration_sd(self):
        self.assertSemanticTypeRegisteredToFormat(
            SampleData[Kraken2Outputs],
            Kraken2OutputDirectoryFormat
        )

    def test_outputs_semantic_type_to_format_registration_fd(self):
        self.assertSemanticTypeRegisteredToFormat(
            FeatureData[Kraken2Outputs],
            Kraken2OutputDirectoryFormat
        )

    def test_kraken2db_semantic_type_registration(self):
        self.assertRegisteredSemanticType(Kraken2DB)

    def test_kraken2db_semantic_type_to_format_registration(self):
        self.assertSemanticTypeRegisteredToFormat(
            Kraken2DB,
            Kraken2DBDirectoryFormat
        )

    def test_kraken2dbreport_semantic_type_registration(self):
        self.assertRegisteredSemanticType(Kraken2DBReport)

    def test_kraken2dbreport_semantic_type_to_format_registration(self):
        self.assertSemanticTypeRegisteredToFormat(
            Kraken2DBReport,
            Kraken2DBReportDirectoryFormat
        )

    def test_brackendb_semantic_type_registration(self):
        self.assertRegisteredSemanticType(BrackenDB)

    def test_brackendb_semantic_type_to_format_registration(self):
        self.assertSemanticTypeRegisteredToFormat(
            BrackenDB,
            BrackenDBDirectoryFormat
        )


if __name__ == '__main__':
    unittest.main()
