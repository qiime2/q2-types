# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest

from q2_types.sample_data import SampleData
from q2_types.per_sample_sequences import (SequencesWithQuality,
                                           PairedEndSequencesWithQuality)
from q2_types.per_sample_sequences import (
    SingleLanePerSampleSingleEndFastqDirFmt,
    SingleLanePerSamplePairedEndFastqDirFmt
)
from qiime.plugin.testing import TestPluginBase


class TestTypes(TestPluginBase):
    package = "q2_types.per_sample_sequences.tests"

    def test_sequences_with_quality_semantic_type_registration(self):
        self.assertRegisteredSemanticType(SequencesWithQuality)

    def test_paired_end_sequences_with_qual_semantic_type_registration(self):
        self.assertRegisteredSemanticType(PairedEndSequencesWithQuality)

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


if __name__ == '__main__':
    unittest.main()
