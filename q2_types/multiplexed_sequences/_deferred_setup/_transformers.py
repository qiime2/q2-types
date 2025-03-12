# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import gzip
import shutil
import itertools

import pandas as pd
import skbio.io

from qiime2 import Metadata

from q2_types._util import FastqGzFormat

from .. import (
    MultiplexedFastaQualDirFmt,
    MultiplexedSingleEndBarcodeInSequenceDirFmt,
    EMPMultiplexedDirFmt,
    ErrorCorrectionDetailsFmt,
    EMPSingleEndDirFmt,
    EMPSingleEndCasavaDirFmt,
    EMPPairedEndDirFmt,
    EMPPairedEndCasavaDirFmt,
    BarcodePairedSequenceFastqIterator,
    BarcodeSequenceFastqIterator
)
from ...plugin_setup import plugin


def _read_fastq_seqs(filepath):
    # This function is adapted from @jairideout's SO post:
    # http://stackoverflow.com/a/39302117/3424666
    fh = gzip.open(filepath, 'rt')
    for seq_header, seq, qual_header, qual in itertools.zip_longest(*[fh] * 4):
        yield (seq_header.strip(), seq.strip(), qual_header.strip(),
               qual.strip())


@plugin.register_transformer
def _1(df: MultiplexedFastaQualDirFmt) -> \
     MultiplexedSingleEndBarcodeInSequenceDirFmt:
    seqs = open(df.sequences.path_maker())
    qual = open(df.quality.path_maker())

    result = MultiplexedSingleEndBarcodeInSequenceDirFmt()

    with open(result.path / 'forward.fastq.gz', 'wb') as fh:
        for seq in skbio.io.read(seqs, qual=qual, format='fasta',
                                 verify=False):
            seq.write(fh, format='fastq', variant='illumina1.8',
                      compression='gzip')

    return result


# NOTE: a legacy transformer isn't needed for EMPMultiplexedSingleEndDirFmt
# as no artifacts exist in this form, it is used for import only.
@plugin.register_transformer
def _18(dirfmt: EMPSingleEndCasavaDirFmt) -> EMPSingleEndDirFmt:
    # TODO: revisit this API to simpify defining transformers
    result = EMPMultiplexedDirFmt().path

    sequences_fp = str(result / 'sequences.fastq.gz')
    barcodes_fp = str(result / 'barcodes.fastq.gz')
    shutil.copyfile(str(dirfmt.sequences.view(FastqGzFormat)), sequences_fp)
    shutil.copyfile(str(dirfmt.barcodes.view(FastqGzFormat)), barcodes_fp)

    return result


@plugin.register_transformer
def _19(dirfmt: EMPPairedEndCasavaDirFmt) -> EMPPairedEndDirFmt:
    result = EMPMultiplexedDirFmt()
    root = result.path

    forward_fp = str(root / 'forward.fastq.gz')
    reverse_fp = str(root / 'reverse.fastq.gz')
    barcodes_fp = str(root / 'barcodes.fastq.gz')
    shutil.copyfile(str(dirfmt.forward.view(FastqGzFormat)), forward_fp)
    shutil.copyfile(str(dirfmt.reverse.view(FastqGzFormat)), reverse_fp)
    shutil.copyfile(str(dirfmt.barcodes.view(FastqGzFormat)), barcodes_fp)

    return result


@plugin.register_transformer
def _32(data: pd.DataFrame) -> ErrorCorrectionDetailsFmt:
    ff = ErrorCorrectionDetailsFmt()
    Metadata(data).save(str(ff))
    return ff


@plugin.register_transformer
def _33(ff: ErrorCorrectionDetailsFmt) -> pd.DataFrame:
    return Metadata.load(str(ff)).to_dataframe()


@plugin.register_transformer
def _34(ff: ErrorCorrectionDetailsFmt) -> Metadata:
    return Metadata.load(str(ff))


@plugin.register_transformer
def _65(dirfmt: EMPSingleEndDirFmt) -> BarcodeSequenceFastqIterator:
    barcode_generator = _read_fastq_seqs(
        str(dirfmt.barcodes.view(FastqGzFormat)))
    sequence_generator = _read_fastq_seqs(
        str(dirfmt.sequences.view(FastqGzFormat)))
    result = BarcodeSequenceFastqIterator(barcode_generator,
                                          sequence_generator)
    # ensure that dirfmt stays in scope as long as result does so these
    # generators will work.
    result.__dirfmt = dirfmt
    return result


# TODO: remove this when names are aliased
@plugin.register_transformer
def _65_legacy(dirfmt: EMPMultiplexedDirFmt) -> BarcodeSequenceFastqIterator:
    return _65(dirfmt)


@plugin.register_transformer
def _67(dirfmt: EMPPairedEndDirFmt) -> BarcodeSequenceFastqIterator:
    barcode_generator = _read_fastq_seqs(
        str(dirfmt.barcodes.view(FastqGzFormat)))
    sequence_generator = _read_fastq_seqs(
        str(dirfmt.forward.view(FastqGzFormat)))
    result = BarcodeSequenceFastqIterator(barcode_generator,
                                          sequence_generator)
    # ensure that dirfmt stays in scope as long as result does so these
    # generators will work.
    result.__dirfmt = dirfmt
    return result


@plugin.register_transformer
def _68(dirfmt: EMPPairedEndDirFmt) -> BarcodePairedSequenceFastqIterator:
    barcode_generator = _read_fastq_seqs(
        str(dirfmt.barcodes.view(FastqGzFormat)))
    forward_generator = _read_fastq_seqs(
        str(dirfmt.forward.view(FastqGzFormat)))
    reverse_generator = _read_fastq_seqs(
        str(dirfmt.reverse.view(FastqGzFormat)))
    result = BarcodePairedSequenceFastqIterator(barcode_generator,
                                                forward_generator,
                                                reverse_generator)
    # ensure that dirfmt stays in scope as long as result does so these
    # generators will work.
    result.__dirfmt = dirfmt
    return result
