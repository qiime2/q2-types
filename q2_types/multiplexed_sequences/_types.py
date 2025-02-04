# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin import SemanticType


MultiplexedSingleEndBarcodeInSequence = \
    SemanticType('MultiplexedSingleEndBarcodeInSequence')
MultiplexedPairedEndBarcodeInSequence = \
    SemanticType('MultiplexedPairedEndBarcodeInSequence')
RawSequences = SemanticType('RawSequences')
EMPSingleEndSequences = SemanticType('EMPSingleEndSequences')
EMPPairedEndSequences = SemanticType('EMPPairedEndSequences')
ErrorCorrectionDetails = SemanticType('ErrorCorrectionDetails')
