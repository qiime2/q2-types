# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest

from qiime2.plugin.testing import TestPluginBase

from q2_types.multiplexed_sequences import (
    MultiplexedSingleEndBarcodeInSequence,
    MultiplexedPairedEndBarcodeInSequence,
    MultiplexedSingleEndBarcodeInSequenceDirFmt,
    MultiplexedPairedEndBarcodeInSequenceDirFmt,
    EMPSingleEndDirFmt, EMPPairedEndDirFmt,
    ErrorCorrectionDetailsDirFmt, RawSequences,
    EMPSingleEndSequences, EMPPairedEndSequences,
    ErrorCorrectionDetails
)


class TestMultiplexedBarcodeInSequenceTypes(TestPluginBase):
    package = "q2_types.per_sample_sequences.tests"

    def test_single_end_semantic_type_registration(self):
        self.assertRegisteredSemanticType(
            MultiplexedSingleEndBarcodeInSequence)

    def test_paired_end_semantic_type_registration(self):
        self.assertRegisteredSemanticType(
            MultiplexedPairedEndBarcodeInSequence)

    def test_single_end_semantic_type_to_format_registration(self):
        self.assertSemanticTypeRegisteredToFormat(
            MultiplexedSingleEndBarcodeInSequence,
            MultiplexedSingleEndBarcodeInSequenceDirFmt,
        )

    def test_paired_end_semantic_type_to_format_registration(self):
        self.assertSemanticTypeRegisteredToFormat(
            MultiplexedPairedEndBarcodeInSequence,
            MultiplexedPairedEndBarcodeInSequenceDirFmt,
        )

    def test_raw_sequences_semantic_type_registration(self):
        self.assertRegisteredSemanticType(RawSequences)

    def test_emp_single_end_sequences_semantic_type_registration(self):
        self.assertRegisteredSemanticType(EMPSingleEndSequences)

    def test_emp_paired_end_sequences_semantic_type_registration(self):
        self.assertRegisteredSemanticType(EMPPairedEndSequences)

    def test_error_correction_details_semantic_type_registration(self):
        self.assertRegisteredSemanticType(ErrorCorrectionDetails)

    def test_error_correction_details_semantic_type_to_format_reg(self):
        self.assertSemanticTypeRegisteredToFormat(
            ErrorCorrectionDetails,
            ErrorCorrectionDetailsDirFmt)

    def test_emp_paired_end_sequences_semantic_type_to_format_reg(self):
        self.assertSemanticTypeRegisteredToFormat(
            EMPPairedEndSequences,
            EMPPairedEndDirFmt)

    def test_emp_single_end_sequences_semantic_type_to_format_reg(self):
        self.assertSemanticTypeRegisteredToFormat(
            EMPSingleEndSequences,
            EMPSingleEndDirFmt)

    def test_raw_sequences_semantic_type_to_format_registration(self):
        self.assertSemanticTypeRegisteredToFormat(
            RawSequences,
            EMPSingleEndDirFmt)


if __name__ == '__main__':
    unittest.main()
