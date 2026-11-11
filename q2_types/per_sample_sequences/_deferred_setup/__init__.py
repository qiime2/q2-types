# ----------------------------------------------------------------------------
# Copyright (c) 2016-2026, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import importlib
from tempfile import TemporaryDirectory
import os
import gzip

from q2_types.sample_data import SampleData
from q2_types.feature_data import FeatureData
from q2_types.bowtie2 import Bowtie2IndexDirFmt

from .. import (CasavaOneEightSingleLanePerSampleDirFmt,
                CasavaOneEightLanelessPerSampleDirFmt,
                FastqGzFormat, YamlFormat,
                FastqManifestFormat, FastqAbsolutePathManifestFormat,
                SingleLanePerSampleSingleEndFastqDirFmt,
                SingleLanePerSamplePairedEndFastqDirFmt,
                SingleEndFastqManifestPhred33,
                SingleEndFastqManifestPhred64,
                PairedEndFastqManifestPhred33,
                PairedEndFastqManifestPhred64,
                SingleEndFastqManifestPhred33V2,
                SingleEndFastqManifestPhred64V2,
                PairedEndFastqManifestPhred33V2,
                PairedEndFastqManifestPhred64V2,
                QIIME1DemuxFormat, QIIME1DemuxDirFmt,
                SampleIdIndexedSingleEndPerSampleDirFmt,
                MultiMAGSequencesDirFmt, MultiMAGManifestFormat,
                ContigSequencesDirFmt, MultiBowtie2IndexDirFmt,
                BAMFormat, BAMDirFmt, MultiBAMDirFmt,
                MultiFASTADirectoryFormat,
                Sequences, SequencesWithQuality,
                PairedEndSequencesWithQuality,
                JoinedSequencesWithQuality, MAGs, Contigs,
                SingleBowtie2Index, MultiBowtie2Index,
                AlignmentMap, MultiAlignmentMap)

from ...plugin_setup import plugin


plugin.register_formats(
    FastqManifestFormat, FastqAbsolutePathManifestFormat, YamlFormat,
    FastqGzFormat, CasavaOneEightSingleLanePerSampleDirFmt,
    CasavaOneEightLanelessPerSampleDirFmt,
    SingleLanePerSampleSingleEndFastqDirFmt,
    SingleLanePerSamplePairedEndFastqDirFmt, SingleEndFastqManifestPhred33,
    SingleEndFastqManifestPhred64, PairedEndFastqManifestPhred33,
    PairedEndFastqManifestPhred64, SingleEndFastqManifestPhred33V2,
    SingleEndFastqManifestPhred64V2, PairedEndFastqManifestPhred33V2,
    PairedEndFastqManifestPhred64V2, QIIME1DemuxFormat, QIIME1DemuxDirFmt,
    SampleIdIndexedSingleEndPerSampleDirFmt, MultiFASTADirectoryFormat,
    MultiMAGSequencesDirFmt, ContigSequencesDirFmt, MultiBowtie2IndexDirFmt,
    BAMFormat, BAMDirFmt, MultiBAMDirFmt, MultiMAGManifestFormat
)

plugin.register_semantic_types(
    Sequences, SequencesWithQuality, PairedEndSequencesWithQuality,
    JoinedSequencesWithQuality, MAGs, Contigs, SingleBowtie2Index,
    MultiBowtie2Index, AlignmentMap, MultiAlignmentMap)


def sequences_with_quality_usage(use):
    with TemporaryDirectory() as tempdir:
        def factory():
            fp = os.path.join(tempdir, 'sample1_S1_L001_R1_001.fastq.gz')
            manifest_fp = os.path.join(tempdir, 'MANIFEST')
            metadata_fp = os.path.join(tempdir, 'metadata.yml')

            with gzip.open(fp, 'w') as f:
                f.write(b'@1\nACTG\n+\nIIII\n')
            with open(manifest_fp, 'w') as f:
                f.write('sample-id,filename,direction\n')
                f.write('sample1,sample1_S1_L001_R1_001.fastq.gz,forward\n')
            with open(metadata_fp, 'w') as f:
                f.write('{phred-offset: 33}')

            ff = SingleLanePerSampleSingleEndFastqDirFmt(tempdir, 'r')
            return ff

        to_import = use.init_format(
            'my_sequences', factory=factory, ext='fastq.gz'
        )
        use.import_from_format(
            'sequences_with_quality',
            semantic_type='SampleData[SequencesWithQuality]',
            variable=to_import,
            view_type='SingleLanePerSampleSingleEndFastqDirFmt'
        )


def joined_sequences_with_quality_usage(use):
    with TemporaryDirectory() as tempdir:
        def factory():
            fp = os.path.join(tempdir, 'sample1_S1_L001_R1_001.fastq.gz')
            manifest_fp = os.path.join(tempdir, 'MANIFEST')
            metadata_fp = os.path.join(tempdir, 'metadata.yml')

            with gzip.open(fp, 'w') as f:
                f.write(b'@1\nACTG\n+\nIIII\n')
            with open(manifest_fp, 'w') as f:
                f.write('sample-id,filename,direction\n')
                f.write('sample1,sample1_S1_L001_R1_001.fastq.gz,forward\n')
            with open(metadata_fp, 'w') as f:
                f.write('{phred-offset: 33}')

            ff = SingleLanePerSampleSingleEndFastqDirFmt(tempdir, 'r')
            return ff

        to_import = use.init_format(
            'my_sequences', factory=factory, ext='fastq.gz'
        )
        use.import_from_format(
            'joined_sequences',
            semantic_type='SampleData[JoinedSequencesWithQuality]',
            variable=to_import,
            view_type='SingleLanePerSampleSingleEndFastqDirFmt'
        )


def paired_end_sequences_with_quality_usage(use):
    with TemporaryDirectory() as tempdir:
        def factory():
            fp_f = os.path.join(tempdir, 'sample1_S1_L001_R1_001.fastq.gz')
            fp_r = os.path.join(tempdir, 'sample1_S1_L001_R2_001.fastq.gz')
            manifest_fp = os.path.join(tempdir, 'MANIFEST')
            metadata_fp = os.path.join(tempdir, 'metadata.yml')

            with gzip.open(fp_f, 'w') as f:
                f.write(b'@1\nACTG\n+\nIIII\n')
            with gzip.open(fp_r, 'w') as f:
                f.write(b'@1\nTGAC\n+\nIIII\n')
            with open(manifest_fp, 'w') as f:
                f.write('sample-id,filename,direction\n')
                f.write('sample1,sample1_S1_L001_R1_001.fastq.gz,forward\n')
                f.write('sample1,sample1_S1_L001_R2_001.fastq.gz,reverse\n')
            with open(metadata_fp, 'w') as f:
                f.write('{phred-offset: 33}')

            ff = SingleLanePerSamplePairedEndFastqDirFmt(tempdir, 'r')
            return ff

        to_import = use.init_format(
            'my_sequences', factory=factory, ext='fastq.gz'
        )
        use.import_from_format(
            'paired_end_sequences',
            semantic_type='SampleData[PairedEndSequencesWithQuality]',
            variable=to_import,
            view_type='SingleLanePerSamplePairedEndFastqDirFmt'
        )


plugin.register_artifact_class(
    SampleData[Sequences],
    directory_format=QIIME1DemuxDirFmt,
    description=("Collections of sequences associated with specified samples "
                 "(i.e., demultiplexed sequences).")
)
plugin.register_artifact_class(
    SampleData[SequencesWithQuality],
    directory_format=SingleLanePerSampleSingleEndFastqDirFmt,
    description=("Collections of sequences with quality scores associated "
                 "with specified samples (i.e., demultiplexed sequences)."),
    examples={'Import sequences with quality': sequences_with_quality_usage}
)
plugin.register_artifact_class(
    SampleData[JoinedSequencesWithQuality],
    directory_format=SingleLanePerSampleSingleEndFastqDirFmt,
    description=("Collections of joined paired-end sequences with quality "
                 "scores associated with specified samples (i.e., "
                 "demultiplexed sequences)."),
    examples={
        'Import joined sequences with quality':
            joined_sequences_with_quality_usage
    }
)
plugin.register_artifact_class(
    SampleData[PairedEndSequencesWithQuality],
    directory_format=SingleLanePerSamplePairedEndFastqDirFmt,
    description=("Collections of unjoined paired-end sequences with quality "
                 "scores associated with specified samples (i.e., "
                 "demultiplexed sequences)."),
    examples={
        'Import paired end sequences with quality':
            paired_end_sequences_with_quality_usage
    }
)
plugin.register_semantic_type_to_format(
    SampleData[MAGs],
    artifact_format=MultiMAGSequencesDirFmt
)
plugin.register_semantic_type_to_format(
    SampleData[Contigs],
    artifact_format=ContigSequencesDirFmt
)
plugin.register_semantic_type_to_format(
    SampleData[SingleBowtie2Index],
    artifact_format=Bowtie2IndexDirFmt
)
plugin.register_semantic_type_to_format(
    SampleData[MultiBowtie2Index],
    artifact_format=MultiBowtie2IndexDirFmt
)
plugin.register_semantic_type_to_format(
    SampleData[AlignmentMap],
    artifact_format=BAMDirFmt
)
plugin.register_semantic_type_to_format(
    FeatureData[AlignmentMap],
    artifact_format=BAMDirFmt
)
plugin.register_semantic_type_to_format(
    SampleData[MultiAlignmentMap],
    artifact_format=MultiBAMDirFmt
)

importlib.import_module('._transformers', __name__)
