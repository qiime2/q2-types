# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest

from q2_types.bowtie2 import Bowtie2IndexDirFmt
from q2_types.feature_data import FeatureData
from q2_types.sample_data import SampleData
from q2_types.per_sample_sequences import (
    Sequences, SequencesWithQuality, PairedEndSequencesWithQuality,
    JoinedSequencesWithQuality, QIIME1DemuxDirFmt,
    SingleLanePerSampleSingleEndFastqDirFmt,
    SingleLanePerSamplePairedEndFastqDirFmt,
    MAGs, MultiMAGSequencesDirFmt,
    Contigs, ContigSequencesDirFmt,
    SingleBowtie2Index, MultiBowtie2Index, MultiBowtie2IndexDirFmt, BAMDirFmt,
    MultiBAMDirFmt, AlignmentMap, MultiAlignmentMap
)
from qiime2.plugin.testing import TestPluginBase


class TestTypes(TestPluginBase):
    package = "q2_types.per_sample_sequences.tests"

    def test_sequences_semantic_type_registration(self):
        self.assertRegisteredSemanticType(Sequences)

    def test_sequences_with_quality_semantic_type_registration(self):
        self.assertRegisteredSemanticType(SequencesWithQuality)

    def test_paired_end_sequences_with_qual_semantic_type_registration(self):
        self.assertRegisteredSemanticType(PairedEndSequencesWithQuality)

    def test_joined_sequences_with_qual_semantic_type_registration(self):
        self.assertRegisteredSemanticType(JoinedSequencesWithQuality)

    def test_sequences_semantic_type_to_format_registration(self):
        self.assertSemanticTypeRegisteredToFormat(
            SampleData[Sequences],
            QIIME1DemuxDirFmt)

    def test_sequences_with_quality_semantic_type_to_format_registration(self):
        self.assertSemanticTypeRegisteredToFormat(
            SampleData[SequencesWithQuality],
            SingleLanePerSampleSingleEndFastqDirFmt
        )

    def test_paired_end_sequences_semantic_type_to_format_registration(self):
        self.assertSemanticTypeRegisteredToFormat(
            SampleData[PairedEndSequencesWithQuality],
            SingleLanePerSamplePairedEndFastqDirFmt
        )

    def test_joined_sequences_with_quality_semantic_type_to_format_reg(self):
        self.assertSemanticTypeRegisteredToFormat(
            SampleData[JoinedSequencesWithQuality],
            SingleLanePerSampleSingleEndFastqDirFmt
        )

    def test_mags_semantic_type_registration(self):
        self.assertRegisteredSemanticType(MAGs)

    def test_mags_semantic_type_to_format_registration(self):
        self.assertSemanticTypeRegisteredToFormat(
            SampleData[MAGs],
            MultiMAGSequencesDirFmt
        )

    def test_contigs_semantic_type_registration(self):
        self.assertRegisteredSemanticType(Contigs)

    def test_contigs_semantic_type_to_format_registration(self):
        self.assertSemanticTypeRegisteredToFormat(
            SampleData[Contigs],
            ContigSequencesDirFmt
        )

    def test_singlebowtie_semantic_type_registration(self):
        self.assertRegisteredSemanticType(SingleBowtie2Index)

    def test_singlebowtie_sd_semantic_type_to_format_registration(self):
        self.assertSemanticTypeRegisteredToFormat(
            SampleData[SingleBowtie2Index],
            Bowtie2IndexDirFmt
        )

    def test_singlebowtie_fd_semantic_type_to_format_registration(self):
        self.assertSemanticTypeRegisteredToFormat(
            FeatureData[SingleBowtie2Index],
            Bowtie2IndexDirFmt
        )

    def test_multibowtie_index_semantic_type_registration(self):
        self.assertRegisteredSemanticType(MultiBowtie2Index)

    def test_multibowtie_index_semantic_type_to_format_registration(self):
        self.assertSemanticTypeRegisteredToFormat(
            SampleData[MultiBowtie2Index],
            MultiBowtie2IndexDirFmt
        )

    def test_aln_map_semantic_type_registration(self):
        self.assertRegisteredSemanticType(AlignmentMap)

    def test_aln_map_sd_semantic_type_to_format_registration(self):
        self.assertSemanticTypeRegisteredToFormat(
            SampleData[AlignmentMap],
            BAMDirFmt
        )

    def test_aln_map_fd_semantic_type_to_format_registration(self):
        self.assertSemanticTypeRegisteredToFormat(
            FeatureData[AlignmentMap],
            BAMDirFmt
        )

    def test_multi_aln_map_semantic_type_registration(self):
        self.assertRegisteredSemanticType(MultiAlignmentMap)

    def test_multi_aln_map_semantic_type_to_format_registration(self):
        self.assertSemanticTypeRegisteredToFormat(
            SampleData[MultiAlignmentMap],
            MultiBAMDirFmt
        )


if __name__ == '__main__':
    unittest.main()
