# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
from q2_types.bowtie2 import Bowtie2IndexDirFmt
from q2_types.sample_data import SampleData
from q2_types.feature_data import BLAST6
from qiime2.core.type import SemanticType

from ..genome_data import SeedOrthologDirFmt
from . import (
    MultiMAGSequencesDirFmt, ContigSequencesDirFmt, MultiBowtie2IndexDirFmt,
    BAMDirFmt, MultiBAMDirFmt
)
from ..plugin_setup import plugin

MAGs = SemanticType(
    'MAGs', variant_of=SampleData.field['type'])
Contigs = SemanticType(
    'Contigs', variant_of=SampleData.field['type'])
SingleBowtie2Index = SemanticType(
    'SingleBowtie2Index', variant_of=SampleData.field['type'])
MultiBowtie2Index = SemanticType(
    'MultiBowtie2Index', variant_of=SampleData.field['type'])
AlignmentMap = SemanticType(
    'AlignmentMap', variant_of=SampleData.field['type'])
MultiAlignmentMap = SemanticType(
    'MultiAlignmentMap', variant_of=SampleData.field['type'])

plugin.register_semantic_types(
    MAGs, Contigs, SingleBowtie2Index, MultiBowtie2Index,
    AlignmentMap, MultiAlignmentMap
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
    SampleData[MultiAlignmentMap],
    artifact_format=MultiBAMDirFmt
)

plugin.register_semantic_type_to_format(
    SampleData[BLAST6],
    artifact_format=SeedOrthologDirFmt
)
