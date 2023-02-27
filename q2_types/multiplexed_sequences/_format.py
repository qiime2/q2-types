# ----------------------------------------------------------------------------
# Copyright (c) 2016-2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import qiime2.plugin.model as model

from ..per_sample_sequences import FastqGzFormat
from ..feature_data import FASTAFormat, DNAFASTAFormat

from ..plugin_setup import plugin


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


class QualFormat(FASTAFormat):
    # qual files (as in the 454 fasta/qual format) look like fasta files
    # except that instead of sequence data they have space separated PHRED
    # scores.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.alphabet = "0123456789 "


class MultiplexedFastaQualDirFmt(model.DirectoryFormat):
    sequences = model.File('reads.fasta', format=DNAFASTAFormat)
    quality = model.File('reads.qual', format=QualFormat)


plugin.register_formats(
    MultiplexedSingleEndBarcodeInSequenceDirFmt,
    MultiplexedPairedEndBarcodeInSequenceDirFmt,
    MultiplexedFastaQualDirFmt
)
