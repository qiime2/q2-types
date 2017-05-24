# ----------------------------------------------------------------------------
# Copyright (c) 2016-2017, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest

from q2_types.feature_data import (
    FeatureData, Taxonomy, Sequence, PairedEndSequence, AlignedSequence,
    TSVTaxonomyDirectoryFormat, DNASequencesDirectoryFormat,
    PairedDNASequencesDirectoryFormat, AlignedDNASequencesDirectoryFormat
)
from qiime2.plugin.testing import TestPluginBase


class TestTypes(TestPluginBase):
    package = 'q2_types.feature_data.tests'

    def test_feature_data_semantic_type_registration(self):
        self.assertRegisteredSemanticType(FeatureData)

    def test_taxonomy_semantic_type_registration(self):
        self.assertRegisteredSemanticType(Taxonomy)

    def test_sequence_semantic_type_registration(self):
        self.assertRegisteredSemanticType(Sequence)

    def test_paired_end_sequence_semantic_type_registration(self):
        self.assertRegisteredSemanticType(PairedEndSequence)

    def test_aligned_sequence_semantic_type_registration(self):
        self.assertRegisteredSemanticType(AlignedSequence)

    def test_taxonomy_semantic_type_to_format_registration(self):
        self.assertSemanticTypeRegisteredToFormat(
                FeatureData[Taxonomy], TSVTaxonomyDirectoryFormat)

    def test_sequence_semantic_type_to_format_registration(self):
        self.assertSemanticTypeRegisteredToFormat(
                FeatureData[Sequence], DNASequencesDirectoryFormat)

    def test_paired_end_sequence_semantic_type_to_format_registration(self):
        self.assertSemanticTypeRegisteredToFormat(
                FeatureData[PairedEndSequence],
                PairedDNASequencesDirectoryFormat
        )

    def test_aligned_sequence_semantic_type_to_format_registration(self):
        self.assertSemanticTypeRegisteredToFormat(
                FeatureData[AlignedSequence],
                AlignedDNASequencesDirectoryFormat
        )


if __name__ == "__main__":
    unittest.main()
