# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime.plugin import SemanticType

from ..plugin_setup import plugin
from . import FeatureTableDirectoryFormatV1, FeatureTableDirectoryFormatV210


FeatureTable = SemanticType('FeatureTable', field_names='content')

Frequency = SemanticType('Frequency', variant_of=FeatureTable.field['content'])

RelativeFrequency = SemanticType('RelativeFrequency',
                                 variant_of=FeatureTable.field['content'])

PresenceAbsence = SemanticType('PresenceAbsence',
                               variant_of=FeatureTable.field['content'])


plugin.register_semantic_type(FeatureTable)
plugin.register_semantic_type(Frequency)
plugin.register_semantic_type(RelativeFrequency)
plugin.register_semantic_type(PresenceAbsence)

plugin.register_semantic_type_to_format(
    FeatureTable[Frequency | RelativeFrequency | PresenceAbsence],
    artifact_format=FeatureTableDirectoryFormatV1
)

plugin.register_semantic_type_to_format(
    FeatureTable[Frequency | RelativeFrequency | PresenceAbsence],
    artifact_format=FeatureTableDirectoryFormatV210
)
