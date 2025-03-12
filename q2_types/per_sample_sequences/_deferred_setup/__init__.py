# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import importlib

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
                 "with specified samples (i.e., demultiplexed sequences).")
)
plugin.register_artifact_class(
    SampleData[JoinedSequencesWithQuality],
    directory_format=SingleLanePerSampleSingleEndFastqDirFmt,
    description=("Collections of joined paired-end sequences with quality "
                 "scores associated with specified samples (i.e., "
                 "demultiplexed sequences).")
)
plugin.register_artifact_class(
    SampleData[PairedEndSequencesWithQuality],
    directory_format=SingleLanePerSamplePairedEndFastqDirFmt,
    description=("Collections of unjoined paired-end sequences with quality "
                 "scores associated with specified samples (i.e., "
                 "demultiplexed sequences).")
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
