# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest

from qiime2.plugin.testing import TestPluginBase

from q2_types.feature_table import (FeatureTable, Frequency,
                                    RelativeFrequency, PercentileNormalized,
                                    Composition, Balance,
                                    PresenceAbsence, BIOMV210DirFmt, Design,
                                    Normalized)


class TestTypes(TestPluginBase):
    package = 'q2_types.feature_table.tests'

    def test_feature_table_semantic_type_registration(self):
        self.assertRegisteredSemanticType(FeatureTable)

    def test_frequency_semantic_type_registration(self):
        self.assertRegisteredSemanticType(Frequency)

    def test_relative_frequency_semantic_type_registration(self):
        self.assertRegisteredSemanticType(RelativeFrequency)

    def test_presence_absence_semantic_type_registration(self):
        self.assertRegisteredSemanticType(PresenceAbsence)

    def test_composition_semantic_type_registration(self):
        self.assertRegisteredSemanticType(Composition)

    def test_balance_semantic_type_registration(self):
        self.assertRegisteredSemanticType(Balance)

    def test_normalized_semantic_type_registration(self):
        self.assertRegisteredSemanticType(Normalized)

    def test_feature_table_semantic_type_to_v210_format_registration(self):
        self.assertSemanticTypeRegisteredToFormat(
            FeatureTable[Frequency],
            BIOMV210DirFmt)
        self.assertSemanticTypeRegisteredToFormat(
            FeatureTable[RelativeFrequency],
            BIOMV210DirFmt)
        self.assertSemanticTypeRegisteredToFormat(
            FeatureTable[PresenceAbsence],
            BIOMV210DirFmt)
        self.assertSemanticTypeRegisteredToFormat(
            FeatureTable[Composition],
            BIOMV210DirFmt)
        self.assertSemanticTypeRegisteredToFormat(
            FeatureTable[Balance],
            BIOMV210DirFmt)
        self.assertSemanticTypeRegisteredToFormat(
            FeatureTable[PercentileNormalized],
            BIOMV210DirFmt)
        self.assertSemanticTypeRegisteredToFormat(
            FeatureTable[Design],
            BIOMV210DirFmt)
        self.assertSemanticTypeRegisteredToFormat(
            FeatureTable[Normalized],
            BIOMV210DirFmt)


if __name__ == "__main__":
    unittest.main()
