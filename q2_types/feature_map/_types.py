# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.core.type import SemanticType

FeatureMap = SemanticType("FeatureMap", field_names="type")
MAGtoContigs = SemanticType(
    "MAGtoContigs", variant_of=FeatureMap.field["type"]
)
