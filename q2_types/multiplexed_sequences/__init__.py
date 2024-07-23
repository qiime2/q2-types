# ----------------------------------------------------------------------------
# Copyright (c) 2016-2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import importlib

from ._format import (MultiplexedSingleEndBarcodeInSequenceDirFmt,
                      MultiplexedPairedEndBarcodeInSequenceDirFmt,
                      MultiplexedFastaQualDirFmt,
                      EMPMultiplexedDirFmt,
                      ErrorCorrectionDetailsFmt,
                      ErrorCorrectionDetailsDirFmt,
                      EMPSingleEndDirFmt,
                      EMPSingleEndCasavaDirFmt,
                      EMPPairedEndDirFmt,
                      EMPPairedEndCasavaDirFmt)
from ._type import (MultiplexedSingleEndBarcodeInSequence,
                    MultiplexedPairedEndBarcodeInSequence,
                    RawSequences,
                    EMPSingleEndSequences,
                    EMPPairedEndSequences,
                    ErrorCorrectionDetails)
from ._objects import (BarcodePairedSequenceFastqIterator,
                       BarcodeSequenceFastqIterator)

__all__ = [
    'MultiplexedSingleEndBarcodeInSequence',
    'MultiplexedPairedEndBarcodeInSequence',
    'MultiplexedSingleEndBarcodeInSequenceDirFmt',
    'MultiplexedPairedEndBarcodeInSequenceDirFmt',
    'MultiplexedFastaQualDirFmt',
    'RawSequences', 'EMPSingleEndSequences', 'EMPPairedEndSequences',
    'EMPMultiplexedDirFmt',
    'ErrorCorrectionDetails', 'ErrorCorrectionDetailsFmt',
    'ErrorCorrectionDetailsDirFmt', 'EMPSingleEndDirFmt',
    'EMPSingleEndCasavaDirFmt', 'EMPPairedEndDirFmt',
    'EMPPairedEndCasavaDirFmt',
    'BarcodePairedSequenceFastqIterator',
    'BarcodeSequenceFastqIterator'
]

importlib.import_module('q2_types.multiplexed_sequences._transformer')
