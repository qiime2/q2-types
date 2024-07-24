# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
from qiime2.plugin import SemanticType


ProfileHMM = SemanticType('ProfileHMM', field_names='type')
SingleProtein = SemanticType(
    'SingleProtein', variant_of=ProfileHMM.field['type']
)
SingleDNA = SemanticType(
    'SingleDNA', variant_of=ProfileHMM.field['type']
)
SingleRNA = SemanticType(
    'SingleRNA', variant_of=ProfileHMM.field['type']
)
MultipleProtein = SemanticType(
    'MultipleProtein', variant_of=ProfileHMM.field['type']
)
MultipleDNA = SemanticType(
    'MultipleDNA', variant_of=ProfileHMM.field['type']
)
MultipleRNA = SemanticType(
    'MultipleRNA', variant_of=ProfileHMM.field['type']
)
PressedProtein = SemanticType(
    'PressedProtein', variant_of=ProfileHMM.field['type']
)
PressedDNA = SemanticType(
    'PressedDNA', variant_of=ProfileHMM.field['type']
)
PressedRNA = SemanticType(
    'PressedRNA', variant_of=ProfileHMM.field['type']
)
