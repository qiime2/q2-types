# ----------------------------------------------------------------------------
# Copyright (c) 2016-2022, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import skbio.io

from . import (MultiplexedFastaQualDirFmt,
               MultiplexedSingleEndBarcodeInSequenceDirFmt)

from ..plugin_setup import plugin


@plugin.register_transformer
def _1(df: MultiplexedFastaQualDirFmt) -> \
     MultiplexedSingleEndBarcodeInSequenceDirFmt:
    seqs = open(df.sequences.path_maker())
    qual = open(df.quality.path_maker())

    result = MultiplexedSingleEndBarcodeInSequenceDirFmt()

    # TODO: can I access the file name (forward.fastq.gz) from result
    # so I'm not duplicating that here?
    with open(result.path / 'forward.fastq.gz', 'wb') as fh:
        for seq in skbio.io.read(seqs, qual=qual, format='fasta',
                                 verify=False):
            seq.write(fh, format='fastq', variant='illumina1.8',
                      compression='gzip')

    return result
