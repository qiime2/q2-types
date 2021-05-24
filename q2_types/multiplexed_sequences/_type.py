# ----------------------------------------------------------------------------
# Copyright (c) 2016-2021, QIIME 2 development team.
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

plugin.register_semantic_type_to_format(
    MultiplexedSingleEndBarcodeInSequence,
    artifact_format=MultiplexedSingleEndBarcodeInSequenceDirFmt
)
plugin.register_semantic_type_to_format(
    MultiplexedPairedEndBarcodeInSequence,
    artifact_format=MultiplexedPairedEndBarcodeInSequenceDirFmt,
)
