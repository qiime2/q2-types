# ----------------------------------------------------------------------------
# Copyright (c) 2016-2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from q2_types.bowtie2 import Bowtie2IndexDirFmt
from q2_types.feature_data import FeatureData
from qiime2.plugin import SemanticType

from ..plugin_setup import plugin
from ..sample_data import SampleData
from . import (QIIME1DemuxDirFmt, SingleLanePerSampleSingleEndFastqDirFmt,
               SingleLanePerSamplePairedEndFastqDirFmt,
               MultiMAGSequencesDirFmt, ContigSequencesDirFmt,
               MultiBowtie2IndexDirFmt, BAMDirFmt, MultiBAMDirFmt)


Sequences = SemanticType('Sequences', variant_of=SampleData.field['type'])
SequencesWithQuality = SemanticType(
    'SequencesWithQuality', variant_of=SampleData.field['type'])
PairedEndSequencesWithQuality = SemanticType(
    'PairedEndSequencesWithQuality', variant_of=SampleData.field['type'])
JoinedSequencesWithQuality = SemanticType(
    'JoinedSequencesWithQuality', variant_of=SampleData.field['type'])
MAGs = SemanticType(
    'MAGs', variant_of=SampleData.field['type'])
Contigs = SemanticType(
    'Contigs', variant_of=SampleData.field['type'])
SingleBowtie2Index = SemanticType(
    'SingleBowtie2Index',
    variant_of=[SampleData.field['type'], FeatureData.field['type']]
)
MultiBowtie2Index = SemanticType(
    'MultiBowtie2Index', variant_of=SampleData.field['type'])
AlignmentMap = SemanticType(
    'AlignmentMap',
    variant_of=[SampleData.field['type'], FeatureData.field['type']]
)
MultiAlignmentMap = SemanticType(
    'MultiAlignmentMap', variant_of=SampleData.field['type'])

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
