# ----------------------------------------------------------------------------
# Copyright (c) 2016-2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest

import pandas as pd
from qiime2.core.exceptions import ValidationError

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

from q2_types.feature_data._type import \
    validate_seq_char_len


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

    def test_validate_sequence_characteristics_length(self):
        data = self._setup_df()
        validate_seq_char_len(data, None)

    def test_validate_sequence_characteristics_length_no_length_column(self):
        data = self._setup_df()
        data.drop(columns=['length'], inplace=True)
        self._assert_validation_error(data, "Column 'length' has to exist in "
                                            "the file.")

    def test_validate_sequence_characteristics_length_not_numerical(self):
        data = self._setup_df()
        data.loc[1, 'length'] = 'a'
        self._assert_validation_error(data, "Values in column 'length' have "
                                            "to be numerical.")

    def test_validate_sequence_characteristics_length_empty_values(self):
        data = self._setup_df()
        data.loc[1, 'length'] = None
        self._assert_validation_error(data, "Column 'length' cannot contain "
                                            "empty (NaN) values.")

    def test_validate_sequence_characteristics_length_negative_values(self):
        data = self._setup_df()
        data.loc[1, 'length'] = -1
        self._assert_validation_error(data, "Column 'length' cannot contain "
                                            "negative values.")

    def _setup_df(self):
        data_path = self.get_data_path("sequence_characteristics_length.tsv")
        return pd.read_csv(data_path, sep="\t", index_col=0)

    def _assert_validation_error(self, data, error_message):
        with self.assertRaises(ValidationError) as context:
            validate_seq_char_len(data, None)
        self.assertEqual(str(context.exception), error_message)


if __name__ == "__main__":
    unittest.main()
