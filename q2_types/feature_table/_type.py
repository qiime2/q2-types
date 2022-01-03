# ----------------------------------------------------------------------------
# Copyright (c) 2016-2022, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin import SemanticType

from ..plugin_setup import plugin
from . import BIOMV210DirFmt


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

plugin.register_semantic_types(FeatureTable, Frequency, RelativeFrequency,
                               PresenceAbsence, Balance, Composition,
                               PercentileNormalized, Design)

plugin.register_semantic_type_to_format(
    FeatureTable[Frequency | RelativeFrequency |
                 PresenceAbsence | Balance | Composition |
                 PercentileNormalized | Design],
    artifact_format=BIOMV210DirFmt
)
