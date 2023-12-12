# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.core.type import SemanticType

from ._format import MAGtoContigsDirFmt
from ..plugin_setup import plugin

FeatureMap = SemanticType("FeatureMap", field_names="type")
MAGtoContigs = SemanticType(
    "MAGtoContigs", variant_of=FeatureMap.field["type"]
)

plugin.register_semantic_types(FeatureMap, MAGtoContigs)
plugin.register_semantic_type_to_format(
    FeatureMap[MAGtoContigs], artifact_format=MAGtoContigsDirFmt
)
