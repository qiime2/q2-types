# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from q2_types.feature_data import FeatureData

from q2_types.feature_data_mag._format import MAGSequencesDirFmt
from qiime2.core.type import SemanticType

from ..bowtie2 import Bowtie2IndexDirFmt
from ..per_sample_sequences import ContigSequencesDirFmt, SingleBowtie2Index
from ..plugin_setup import plugin


MAG = SemanticType('MAG', variant_of=FeatureData.field['type'])

plugin.register_semantic_types(MAG)
plugin.register_semantic_type_to_format(
    FeatureData[MAG],
    artifact_format=MAGSequencesDirFmt
)

Contig = SemanticType('Contig', variant_of=FeatureData.field['type'])

plugin.register_semantic_types(Contig)
plugin.register_semantic_type_to_format(
    FeatureData[Contig],
    artifact_format=ContigSequencesDirFmt
)

plugin.register_semantic_type_to_format(
    FeatureData[SingleBowtie2Index],
    artifact_format=Bowtie2IndexDirFmt
)
