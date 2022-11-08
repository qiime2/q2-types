# ----------------------------------------------------------------------------
# Copyright (c) 2016-2022, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import importlib

from ._format import (MultiplexedSingleEndBarcodeInSequenceDirFmt,
                      MultiplexedPairedEndBarcodeInSequenceDirFmt,
                      MultiplexedFastaQualDirFmt)
from ._type import (MultiplexedSingleEndBarcodeInSequence,
                    MultiplexedPairedEndBarcodeInSequence)

__all__ = [
    'MultiplexedSingleEndBarcodeInSequence',
    'MultiplexedPairedEndBarcodeInSequence',
    'MultiplexedSingleEndBarcodeInSequenceDirFmt',
    'MultiplexedPairedEndBarcodeInSequenceDirFmt',
    'MultiplexedFastaQualDirFmt'
]

importlib.import_module('q2_types.multiplexed_sequences._transformer')
