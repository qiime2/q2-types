# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin import SemanticType

from ..plugin_setup import plugin
from . import ReferenceFeaturesDirectoryFormat


ReferenceFeatures = SemanticType('ReferenceFeatures', field_names='type')
SSU = SemanticType('SSU', variant_of=ReferenceFeatures.field['type'])

plugin.register_semantic_types(ReferenceFeatures, SSU)

plugin.register_semantic_type_to_format(
    ReferenceFeatures[SSU],
    artifact_format=ReferenceFeaturesDirectoryFormat)
