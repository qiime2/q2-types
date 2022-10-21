# ----------------------------------------------------------------------------
# Copyright (c) 2016-2022, QIIME 2 development team.
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


class MultiplexedFastaQualDirFmt(model.DirectoryFormat):
    sequences = model.File('seqs.fna', format=DNAFASTAFormat)
    # should probably have a QualFormat for validation purposes
    # how to do cross-file validation (i.e., at the level of the DirFormat)
    quality = model.File('seqs.qual', format=FASTAFormat)


plugin.register_formats(
    MultiplexedSingleEndBarcodeInSequenceDirFmt,
    MultiplexedPairedEndBarcodeInSequenceDirFmt,
    MultiplexedFastaQualDirFmt
)
