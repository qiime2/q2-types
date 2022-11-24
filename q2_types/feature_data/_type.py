# ----------------------------------------------------------------------------
# Copyright (c) 2016-2022, QIIME 2 development team.
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
               AlignedProteinSequencesDirectoryFormat,
               RNASequencesDirectoryFormat, AlignedRNASequencesDirectoryFormat,
               PairedRNASequencesDirectoryFormat, BLAST6DirectoryFormat)


FeatureData = SemanticType('FeatureData', field_names='type')

Taxonomy = SemanticType('Taxonomy', variant_of=FeatureData.field['type'])

Sequence = SemanticType('Sequence', variant_of=FeatureData.field['type'])

RNASequence = SemanticType('RNASequence', variant_of=FeatureData.field['type'])

PairedEndSequence = SemanticType('PairedEndSequence',
                                 variant_of=FeatureData.field['type'])

PairedEndRNASequence = SemanticType('PairedEndRNASequence',
                                    variant_of=FeatureData.field['type'])

AlignedSequence = SemanticType('AlignedSequence',
                               variant_of=FeatureData.field['type'])

AlignedRNASequence = SemanticType('AlignedRNASequence',
                                  variant_of=FeatureData.field['type'])

Differential = SemanticType('Differential',
                            variant_of=FeatureData.field['type'])

ProteinSequence = SemanticType('ProteinSequence',
                               variant_of=FeatureData.field['type'])

AlignedProteinSequence = SemanticType('AlignedProteinSequence',
                                      variant_of=FeatureData.field['type'])

BLAST6 = SemanticType('BLAST6', variant_of=FeatureData.field['type'])

plugin.register_semantic_types(FeatureData, Taxonomy, Sequence,
                               PairedEndSequence, AlignedSequence,
                               Differential, ProteinSequence,
                               AlignedProteinSequence, RNASequence,
                               AlignedRNASequence, PairedEndRNASequence,
                               BLAST6)


plugin.register_artifact_class(
    FeatureData[Taxonomy],
    directory_format=TSVTaxonomyDirectoryFormat)
plugin.register_artifact_class(
    FeatureData[Sequence],
    directory_format=DNASequencesDirectoryFormat)
plugin.register_artifact_class(
    FeatureData[RNASequence],
    directory_format=RNASequencesDirectoryFormat)
plugin.register_artifact_class(
    FeatureData[PairedEndSequence],
    directory_format=PairedDNASequencesDirectoryFormat)
plugin.register_artifact_class(
    FeatureData[PairedEndRNASequence],
    directory_format=PairedRNASequencesDirectoryFormat)
plugin.register_artifact_class(
    FeatureData[AlignedSequence],
    directory_format=AlignedDNASequencesDirectoryFormat)
plugin.register_artifact_class(
    FeatureData[AlignedRNASequence],
    directory_format=AlignedRNASequencesDirectoryFormat)
plugin.register_artifact_class(
    FeatureData[Differential], DifferentialDirectoryFormat)
plugin.register_artifact_class(
    FeatureData[ProteinSequence],
    directory_format=ProteinSequencesDirectoryFormat)
plugin.register_artifact_class(
    FeatureData[AlignedProteinSequence],
    directory_format=AlignedProteinSequencesDirectoryFormat)
plugin.register_artifact_class(
    FeatureData[BLAST6],
    directory_format=BLAST6DirectoryFormat)
