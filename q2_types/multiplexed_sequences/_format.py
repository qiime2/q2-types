# ----------------------------------------------------------------------------
# Copyright (c) 2016-2020, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import qiime2.plugin.model as model

from ..plugin_setup import plugin
from q2_types.per_sample_sequences import FastqGzFormat


# MultiplexedSingleEndBarcodeInSequenceDirFmt &
# MultiplexedPairedEndBarcodeInSequenceDirFmt represent multiplexed sequences
# that contain inline barcode information:
# AGGACTAGGTAGATC => barcode: AGGA ; biological sequence: CTAGGTAGATC

MultiplexedSingleEndBarcodeInSequenceDirFmt = model.SingleFileDirectoryFormat(
    'MultiplexedSingleEndBarcodeInSequenceDirFmt', 'forward.fastq.gz',
    FastqGzFormat)


class MultiplexedPairedEndBarcodeInSequenceDirFmt(model.DirectoryFormat):
    forward_sequences = model.File('forward.fastq.gz', format=FastqGzFormat)
    reverse_sequences = model.File('reverse.fastq.gz', format=FastqGzFormat)


plugin.register_formats(
    MultiplexedSingleEndBarcodeInSequenceDirFmt,
    MultiplexedPairedEndBarcodeInSequenceDirFmt,
)
