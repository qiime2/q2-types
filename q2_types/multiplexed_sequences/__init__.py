# ----------------------------------------------------------------------------
# Copyright (c) 2016-2018, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from ._format import (MultiplexedSingleEndBarcodeInSequenceDirFmt,
                      MultiplexedPairedEndBarcodeInSequenceDirFmt)
from ._type import (MultiplexedSingleEndBarcodeInSequence,
                    MultiplexedPairedEndBarcodeInSequence)

__all__ = [
    'MultiplexedSingleEndBarcodeInSequence',
    'MultiplexedPairedEndBarcodeInSequence',
    'MultiplexedSingleEndBarcodeInSequenceDirFmt',
    'MultiplexedPairedEndBarcodeInSequenceDirFmt',
]
