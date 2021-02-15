# ----------------------------------------------------------------------------
# Copyright (c) 2016-2021, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin import SemanticType

from ..plugin_setup import plugin
from . import (TSVTaxonomyDirectoryFormat, DNASequencesDirectoryFormat,
               PairedDNASequencesDirectoryFormat,
               AlignedDNASequencesDirectoryFormat,
               DifferentialDirectoryFormat, ProteinSequencesDirectoryFormat,
               AlignedProteinSequencesDirectoryFormat)


FeatureData = SemanticType('FeatureData', field_names='type')

Taxonomy = SemanticType('Taxonomy', variant_of=FeatureData.field['type'])

Sequence = SemanticType('Sequence', variant_of=FeatureData.field['type'])

PairedEndSequence = SemanticType('PairedEndSequence',
                                 variant_of=FeatureData.field['type'])

AlignedSequence = SemanticType('AlignedSequence',
                               variant_of=FeatureData.field['type'])

Differential = SemanticType('Differential',
                            variant_of=FeatureData.field['type'])

ProteinSequence = SemanticType('ProteinSequence',
                               variant_of=FeatureData.field['type'])

AlignedProteinSequence = SemanticType('AlignedProteinSequence',
                                      variant_of=FeatureData.field['type'])

plugin.register_semantic_types(FeatureData, Taxonomy, Sequence,
                               PairedEndSequence, AlignedSequence,
                               Differential, ProteinSequence,
                               AlignedProteinSequence)


plugin.register_semantic_type_to_format(
    FeatureData[Taxonomy],
    artifact_format=TSVTaxonomyDirectoryFormat)
plugin.register_semantic_type_to_format(
    FeatureData[Sequence],
    artifact_format=DNASequencesDirectoryFormat)
plugin.register_semantic_type_to_format(
    FeatureData[PairedEndSequence],
    artifact_format=PairedDNASequencesDirectoryFormat)
plugin.register_semantic_type_to_format(
    FeatureData[AlignedSequence],
    artifact_format=AlignedDNASequencesDirectoryFormat)
plugin.register_semantic_type_to_format(
    FeatureData[Differential], DifferentialDirectoryFormat)
plugin.register_semantic_type_to_format(
    FeatureData[ProteinSequence],
    artifact_format=ProteinSequencesDirectoryFormat)
plugin.register_semantic_type_to_format(
    FeatureData[AlignedProteinSequence],
    artifact_format=AlignedProteinSequencesDirectoryFormat)
