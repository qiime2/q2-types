# ----------------------------------------------------------------------------
# Copyright (c) 2016-2020, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest

from q2_types.feature_table import (FeatureTable, Frequency,
                                    RelativeFrequency, PercentileNormalized,
                                    Composition, Balance,
                                    PresenceAbsence, BIOMV210DirFmt, Design)
from qiime2.plugin.testing import TestPluginBase


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

    def test_feature_table_semantic_type_to_v210_format_registration(self):
        self.assertSemanticTypeRegisteredToFormat(
            FeatureTable[Frequency | RelativeFrequency | PresenceAbsence |
                         Composition | Balance | PercentileNormalized |
                         Design],
            BIOMV210DirFmt)


if __name__ == "__main__":
    unittest.main()
