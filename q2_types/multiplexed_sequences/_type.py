# ----------------------------------------------------------------------------
# Copyright (c) 2016-2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin import SemanticType

from ..plugin_setup import plugin
from . import (MultiplexedSingleEndBarcodeInSequenceDirFmt,
               MultiplexedPairedEndBarcodeInSequenceDirFmt,
               EMPSingleEndDirFmt,
               EMPPairedEndDirFmt,
               ErrorCorrectionDetailsDirFmt)


MultiplexedSingleEndBarcodeInSequence = \
    SemanticType('MultiplexedSingleEndBarcodeInSequence')
MultiplexedPairedEndBarcodeInSequence = \
    SemanticType('MultiplexedPairedEndBarcodeInSequence')
RawSequences = SemanticType('RawSequences')
EMPSingleEndSequences = SemanticType('EMPSingleEndSequences')
EMPPairedEndSequences = SemanticType('EMPPairedEndSequences')
ErrorCorrectionDetails = SemanticType('ErrorCorrectionDetails')
plugin.register_semantic_types(MultiplexedSingleEndBarcodeInSequence,
                               MultiplexedPairedEndBarcodeInSequence,
                               RawSequences, EMPSingleEndSequences,
                               EMPPairedEndSequences,
                               ErrorCorrectionDetails)

plugin.register_artifact_class(
    MultiplexedSingleEndBarcodeInSequence,
    directory_format=MultiplexedSingleEndBarcodeInSequenceDirFmt,
    description=("Multiplexed sequences (i.e., representing multiple "
                 "difference samples), which are single-end reads, and which "
                 "contain the barcode (i.e., index) indicating the source "
                 "sample as part of the sequence read.")
)
plugin.register_artifact_class(
    MultiplexedPairedEndBarcodeInSequence,
    directory_format=MultiplexedPairedEndBarcodeInSequenceDirFmt,
    description=("Multiplexed sequences (i.e., representing multiple "
                 "difference samples), which are paired-end reads, and which "
                 "contain the barcode (i.e., index) indicating the source "
                 "sample as part of the sequence read.")
)
# TODO: remove when aliasing exists
plugin.register_semantic_type_to_format(
    RawSequences,
    artifact_format=EMPSingleEndDirFmt
)

plugin.register_semantic_type_to_format(
    EMPSingleEndSequences,
    artifact_format=EMPSingleEndDirFmt
)

plugin.register_semantic_type_to_format(
    EMPPairedEndSequences,
    artifact_format=EMPPairedEndDirFmt
)

plugin.register_semantic_type_to_format(
    ErrorCorrectionDetails,
    artifact_format=ErrorCorrectionDetailsDirFmt
)
