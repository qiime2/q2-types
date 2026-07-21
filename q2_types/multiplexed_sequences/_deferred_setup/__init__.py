# ----------------------------------------------------------------------------
# Copyright (c) 2016-2026, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import importlib
import gzip
import os
from tempfile import TemporaryDirectory

from .. import (MultiplexedSingleEndBarcodeInSequenceDirFmt,
                MultiplexedPairedEndBarcodeInSequenceDirFmt,
                MultiplexedFastaQualDirFmt,
                EMPMultiplexedDirFmt,
                ErrorCorrectionDetailsFmt,
                ErrorCorrectionDetailsDirFmt,
                EMPSingleEndDirFmt,
                EMPSingleEndCasavaDirFmt,
                EMPPairedEndDirFmt,
                EMPPairedEndCasavaDirFmt,
                MultiplexedSingleEndBarcodeInSequence,
                MultiplexedPairedEndBarcodeInSequence,
                RawSequences,
                EMPSingleEndSequences,
                EMPPairedEndSequences,
                ErrorCorrectionDetails)

from ...plugin_setup import plugin


plugin.register_formats(
    MultiplexedSingleEndBarcodeInSequenceDirFmt,
    MultiplexedPairedEndBarcodeInSequenceDirFmt,
    MultiplexedFastaQualDirFmt, EMPMultiplexedDirFmt,
    ErrorCorrectionDetailsDirFmt, ErrorCorrectionDetailsFmt,
    EMPSingleEndDirFmt, EMPSingleEndCasavaDirFmt,
    EMPPairedEndDirFmt, EMPPairedEndCasavaDirFmt
)

plugin.register_semantic_types(MultiplexedSingleEndBarcodeInSequence,
                               MultiplexedPairedEndBarcodeInSequence,
                               RawSequences, EMPSingleEndSequences,
                               EMPPairedEndSequences,
                               ErrorCorrectionDetails)


def multiplexed_single_end_barcode_usage(use):
    with TemporaryDirectory() as tempdir:
        def factory():
            fp = os.path.join(tempdir, 'forward.fastq.gz')
            with gzip.open(fp, 'w') as f:
                f.write(b'@1\nATTACGG\n+\nIIIIIII\n')
            ff = MultiplexedSingleEndBarcodeInSequenceDirFmt(tempdir, 'r')

            return ff

        to_import = use.init_format(
            'my_multiplexed_barcode_sequence', factory=factory, ext='.fastq.gz'
        )
        use.import_from_format(
            'multiplexed_barcode_sequence',
            semantic_type='MultiplexedSingleEndBarcodeInSequence',
            variable=to_import,
            view_type='MultiplexedSingleEndBarcodeInSequenceDirFmt'
        )


def multiplexed_paired_end_barcode_usage(use):
    with TemporaryDirectory() as tempdir:
        def factory():
            fp_f = os.path.join(tempdir, 'forward.fastq.gz')
            fp_r = os.path.join(tempdir, 'reverse.fastq.gz')
            with gzip.open(fp_f, 'w') as f:
                f.write(b'@1\nATTACGG\n+\nIIIIIII\n')
            with gzip.open(fp_r, 'w') as f:
                f.write(b'@1\nTAATGCC\n+\nIIIIIII\n')
            ff = MultiplexedSingleEndBarcodeInSequenceDirFmt(tempdir, 'r')

            return ff

        to_import = use.init_format(
            'my_multiplexed_barcode_sequence', factory=factory, ext='.fastq.gz'
        )
        use.import_from_format(
            'multiplexed_barcode_sequence',
            semantic_type='MultiplexedPairedEndBarcodeInSequence',
            variable=to_import,
            view_type='MultiplexedPairedEndBarcodeInSequenceDirFmt'
        )


plugin.register_artifact_class(
    MultiplexedSingleEndBarcodeInSequence,
    directory_format=MultiplexedSingleEndBarcodeInSequenceDirFmt,
    description=("Multiplexed sequences (i.e., representing multiple "
                 "difference samples), which are single-end reads, and which "
                 "contain the barcode (i.e., index) indicating the source "
                 "sample as part of the sequence read."),
    examples={
        'Import multiplexed single end barcode in sequences':
            multiplexed_single_end_barcode_usage
    }
)
plugin.register_artifact_class(
    MultiplexedPairedEndBarcodeInSequence,
    directory_format=MultiplexedPairedEndBarcodeInSequenceDirFmt,
    description=("Multiplexed sequences (i.e., representing multiple "
                 "difference samples), which are paired-end reads, and which "
                 "contain the barcode (i.e., index) indicating the source "
                 "sample as part of the sequence read."),
    examples={
        'Import multiplexed paired end barcode in sequences':
            multiplexed_paired_end_barcode_usage
    }
)
# TODO: remove when aliasing exists
plugin.register_semantic_type_to_format(
    RawSequences,
    artifact_format=EMPSingleEndDirFmt
)

plugin.register_semantic_type_to_format(
    EMPSingleEndSequences,
    artifact_format=EMPSingleEndDirFmt
)

plugin.register_semantic_type_to_format(
    EMPPairedEndSequences,
    artifact_format=EMPPairedEndDirFmt
)

plugin.register_semantic_type_to_format(
    ErrorCorrectionDetails,
    artifact_format=ErrorCorrectionDetailsDirFmt
)

importlib.import_module('._transformers', __name__)
