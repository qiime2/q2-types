# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime.plugin import SemanticType

from ..plugin_setup import plugin
from ._format import (TaxonomyDirectoryFormat, DNASequencesDirectoryFormat,
                      PairedDNASequencesDirectoryFormat,
                      AlignedDNASequencesDirectoryFormat)


FeatureData = SemanticType('FeatureData', field_names='type')

Taxonomy = SemanticType('Taxonomy', variant_of=FeatureData.field['type'])

Sequence = SemanticType('Sequence', variant_of=FeatureData.field['type'])

PairedEndSequence = SemanticType('PairedEndSequence',
                                 variant_of=FeatureData.field['type'])

AlignedSequence = SemanticType('AlignedSequence',
                               variant_of=FeatureData.field['type'])

plugin.register_semantic_type(FeatureData)
plugin.register_semantic_type(Taxonomy)
plugin.register_semantic_type(Sequence)
plugin.register_semantic_type(PairedEndSequence)
plugin.register_semantic_type(AlignedSequence)

plugin.register_semantic_type_to_format(
    FeatureData[Taxonomy],
    artifact_format=TaxonomyDirectoryFormat)
plugin.register_semantic_type_to_format(
    FeatureData[Sequence],
    artifact_format=DNASequencesDirectoryFormat)
plugin.register_semantic_type_to_format(
    FeatureData[PairedEndSequence],
    artifact_format=PairedDNASequencesDirectoryFormat)
plugin.register_semantic_type_to_format(
    FeatureData[AlignedSequence],
    artifact_format=AlignedDNASequencesDirectoryFormat)
