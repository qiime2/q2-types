# ----------------------------------------------------------------------------
# Copyright (c) 2016-2020, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest

from q2_types.multiplexed_sequences import (
    MultiplexedSingleEndBarcodeInSequence,
    MultiplexedPairedEndBarcodeInSequence,
    MultiplexedSingleEndBarcodeInSequenceDirFmt,
    MultiplexedPairedEndBarcodeInSequenceDirFmt,
)
from qiime2.plugin.testing import TestPluginBase


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


if __name__ == '__main__':
    unittest.main()
