# ----------------------------------------------------------------------------
# Copyright (c) 2016-2021, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest

from q2_types.sample_data import SampleData
from q2_types.per_sample_sequences import (
    Sequences, SequencesWithQuality, PairedEndSequencesWithQuality,
    JoinedSequencesWithQuality, QIIME1DemuxDirFmt,
    SingleLanePerSampleSingleEndFastqDirFmt,
    SingleLanePerSamplePairedEndFastqDirFmt
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
            QIIME1DemuxDirFmt
        )

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


if __name__ == '__main__':
    unittest.main()
