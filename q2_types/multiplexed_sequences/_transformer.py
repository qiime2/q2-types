# ----------------------------------------------------------------------------
# Copyright (c) 2016-2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import skbio.io
import pandas as pd

from . import (MultiplexedFastaQualDirFmt,
               MultiplexedSingleEndBarcodeInSequenceDirFmt,
               EMPMultiplexedDirFmt,
               ErrorCorrectionDetailsFmt,
               EMPSingleEndDirFmt,
               EMPSingleEndCasavaDirFmt,
               EMPPairedEndDirFmt,
               EMPPairedEndCasavaDirFmt)
from ..per_sample_sequences import (SingleLanePerSampleSingleEndFastqDirFmt,
                                    SingleLanePerSamplePairedEndFastqDirFmt)
import shutil
from qiime2 import Metadata
from ..feature_data._util import _PlotQualView
from ..plugin_setup import plugin
from .._util import FastqGzFormat


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


# TODO: Remove _PlotQualView once QIIME 2 #220 completed
@plugin.register_transformer
def _30(dirfmt: SingleLanePerSampleSingleEndFastqDirFmt) -> _PlotQualView:
    return _PlotQualView(dirfmt, paired=False)


@plugin.register_transformer
def _31(dirfmt: SingleLanePerSamplePairedEndFastqDirFmt) -> _PlotQualView:
    return _PlotQualView(dirfmt, paired=True)


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
