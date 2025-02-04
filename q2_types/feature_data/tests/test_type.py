# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest


from q2_types.feature_data import (
    FeatureData, Taxonomy, Sequence, PairedEndSequence, AlignedSequence,
    Differential, TSVTaxonomyDirectoryFormat, DNASequencesDirectoryFormat,
    DifferentialDirectoryFormat, PairedDNASequencesDirectoryFormat,
    AlignedDNASequencesDirectoryFormat, ProteinSequencesDirectoryFormat,
    AlignedProteinSequencesDirectoryFormat, ProteinSequence,
    AlignedProteinSequence, RNASequence, RNASequencesDirectoryFormat,
    AlignedRNASequencesDirectoryFormat, AlignedRNASequence,
    PairedRNASequencesDirectoryFormat, PairedEndRNASequence,
    BLAST6, BLAST6DirectoryFormat, SequenceCharacteristics,
    SequenceCharacteristicsDirectoryFormat
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

    def test_differential_semantic_type_registration(self):
        self.assertRegisteredSemanticType(AlignedSequence)

    def test_protein_sequence_semantic_type_registration(self):
        self.assertRegisteredSemanticType(ProteinSequence)

    def test_aligned_protein_sequence_semantic_type_registration(self):
        self.assertRegisteredSemanticType(AlignedProteinSequence)

    def test_differential_semantic_type_to_format_registration(self):
        self.assertSemanticTypeRegisteredToFormat(
                FeatureData[Differential], DifferentialDirectoryFormat)

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

    def test_protein_sequence_semantic_type_to_format_registration(self):
        self.assertSemanticTypeRegisteredToFormat(
                FeatureData[ProteinSequence],
                ProteinSequencesDirectoryFormat
        )

    def test_aln_protein_sequence_semantic_type_to_format_registration(self):
        self.assertSemanticTypeRegisteredToFormat(
                FeatureData[AlignedProteinSequence],
                AlignedProteinSequencesDirectoryFormat
        )

    def test_rna_sequence_semantic_type_registration(self):
        self.assertRegisteredSemanticType(RNASequence)

    def test_aligned_rna_sequence_semantic_type_registration(self):
        self.assertRegisteredSemanticType(AlignedRNASequence)

    def test_paired_end_rna_sequence_semantic_type_registration(self):
        self.assertRegisteredSemanticType(PairedEndRNASequence)

    def test_rna_sequence_semantic_type_to_format_registration(self):
        self.assertSemanticTypeRegisteredToFormat(
                FeatureData[RNASequence], RNASequencesDirectoryFormat)

    def test_paired_end_rna_sequence_semantic_type_to_format_registration(
            self):
        self.assertSemanticTypeRegisteredToFormat(
                FeatureData[PairedEndRNASequence],
                PairedRNASequencesDirectoryFormat
        )

    def test_aligned_rna_sequence_semantic_type_to_format_registration(self):
        self.assertSemanticTypeRegisteredToFormat(
                FeatureData[AlignedRNASequence],
                AlignedRNASequencesDirectoryFormat
        )

    def test_blast6_semantic_type_registration(self):
        self.assertRegisteredSemanticType(BLAST6)

    def test_blast6_semantic_type_to_format_registration(self):
        self.assertSemanticTypeRegisteredToFormat(
                FeatureData[BLAST6], BLAST6DirectoryFormat)

    def test_sequence_characteristics_semantic_type_registration(self):
        self.assertRegisteredSemanticType(SequenceCharacteristics)

    def test_sequence_characteristics_semantic_type_format_registration(self):
        self.assertSemanticTypeRegisteredToFormat(
            FeatureData[SequenceCharacteristics],
            SequenceCharacteristicsDirectoryFormat)


if __name__ == "__main__":
    unittest.main()
