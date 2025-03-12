# ----------------------------------------------------------------------------
# Copyright (c) 2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin import SemanticType

StatsTable = SemanticType('StatsTable', field_names=['kind'])

Pairwise = SemanticType('Pairwise', variant_of=StatsTable.field['kind'])
Global = SemanticType('Global', variant_of=StatsTable.field['kind'])

Dist1D = SemanticType('Dist1D', field_names=['order', 'dependence'])

Ordered = SemanticType('Ordered', variant_of=(Dist1D.field['order']))
Unordered = SemanticType('Unordered', variant_of=(Dist1D.field['order']))
Multi = SemanticType('Multi', variant_of=Dist1D.field['order'])
NestedOrdered = SemanticType('NestedOrdered',
                             variant_of=(Dist1D.field['order']))
NestedUnordered = SemanticType('NestedUnordered',
                               variant_of=(Dist1D.field['order']))

Matched = SemanticType('Matched',
                       variant_of=(Dist1D.field['dependence']))
Independent = SemanticType('Independent',
                           variant_of=(Dist1D.field['dependence']))
