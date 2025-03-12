# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from q2_types.feature_data import FeatureData
from qiime2.plugin import SemanticType

from ..sample_data import SampleData


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
