# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
from qiime2.plugin import SemanticType

from q2_types.feature_data import FeatureData
from q2_types.sample_data import SampleData

Kraken2Reports = SemanticType(
    'Kraken2Report',
    variant_of=[SampleData.field['type'], FeatureData.field['type']]
)
Kraken2Outputs = SemanticType(
    'Kraken2Output',
    variant_of=[SampleData.field['type'], FeatureData.field['type']]
)
Kraken2DB = SemanticType('Kraken2DB')
Kraken2DBReport = SemanticType('Kraken2DBReport')
BrackenDB = SemanticType('BrackenDB')
