# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
from qiime2.plugin import SemanticType


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

BLAST6 = SemanticType('BLAST6',
                      variant_of=FeatureData.field['type'])

SequenceCharacteristics = SemanticType('SequenceCharacteristics',
                                       variant_of=FeatureData.field['type'])
