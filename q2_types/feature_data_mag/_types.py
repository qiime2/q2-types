# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.core.type import SemanticType

from q2_types.feature_data import FeatureData


MAG = SemanticType('MAG', variant_of=FeatureData.field['type'])
Contig = SemanticType('Contig', variant_of=FeatureData.field['type'])
