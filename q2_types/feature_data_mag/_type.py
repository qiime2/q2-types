# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from q2_types.feature_data import FeatureData

from q2_types.feature_data_mag._format import (
        MAGSequencesDirFmt, OrthologAnnotationDirFmt
        )
from qiime2.core.type import SemanticType

from ..per_sample_sequences import ContigSequencesDirFmt
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

NOG = SemanticType('NOG', variant_of=FeatureData.field['type'])

plugin.register_semantic_types(NOG)
plugin.register_artifact_class(
        FeatureData[NOG],
        directory_format=OrthologAnnotationDirFmt)


OG = SemanticType('OG', variant_of=FeatureData.field['type'])

plugin.register_semantic_types(OG)
plugin.register_artifact_class(
        FeatureData[OG],
        directory_format=OrthologAnnotationDirFmt)


KEGG = SemanticType('KEGG', variant_of=FeatureData.field['type'])

plugin.register_semantic_types(KEGG)
plugin.register_artifact_class(
        FeatureData[KEGG],
        directory_format=OrthologAnnotationDirFmt)
