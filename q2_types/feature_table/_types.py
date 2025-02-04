# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin import SemanticType


FeatureTable = SemanticType('FeatureTable', field_names='content')

Frequency = SemanticType('Frequency', variant_of=FeatureTable.field['content'])

RelativeFrequency = SemanticType('RelativeFrequency',
                                 variant_of=FeatureTable.field['content'])

PresenceAbsence = SemanticType('PresenceAbsence',
                               variant_of=FeatureTable.field['content'])

Composition = SemanticType('Composition',
                           variant_of=FeatureTable.field['content'])

Balance = SemanticType('Balance',
                       variant_of=FeatureTable.field['content'])

PercentileNormalized = SemanticType('PercentileNormalized',
                                    variant_of=FeatureTable.field['content'])

# Design is the type of design matrices for linear regressions that have
# been transformed/coded.
Design = SemanticType('Design', variant_of=FeatureTable.field['content'])

Normalized = SemanticType('Normalized',
                          variant_of=FeatureTable.field['content'])
