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
               MultiplexedPairedEndBarcodeInSequenceDirFmt)


MultiplexedSingleEndBarcodeInSequence = \
    SemanticType('MultiplexedSingleEndBarcodeInSequence')
MultiplexedPairedEndBarcodeInSequence = \
    SemanticType('MultiplexedPairedEndBarcodeInSequence')

plugin.register_semantic_types(MultiplexedSingleEndBarcodeInSequence,
                               MultiplexedPairedEndBarcodeInSequence)

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
