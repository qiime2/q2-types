# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
from q2_types.feature_data import FeatureData
from q2_types.sample_data import SampleData
from qiime2.plugin import SemanticType

from . import (
    Kraken2ReportDirectoryFormat, Kraken2OutputDirectoryFormat,
    Kraken2DBDirectoryFormat, Kraken2DBReportDirectoryFormat,
    BrackenDBDirectoryFormat
)
from ..plugin_setup import plugin


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

plugin.register_semantic_types(
    Kraken2Reports, Kraken2Outputs, Kraken2DB, Kraken2DBReport, BrackenDB
)

plugin.register_semantic_type_to_format(
    SampleData[Kraken2Reports],
    artifact_format=Kraken2ReportDirectoryFormat
)
plugin.register_semantic_type_to_format(
    FeatureData[Kraken2Reports],
    artifact_format=Kraken2ReportDirectoryFormat
)
plugin.register_semantic_type_to_format(
    SampleData[Kraken2Outputs],
    artifact_format=Kraken2OutputDirectoryFormat
)
plugin.register_semantic_type_to_format(
    FeatureData[Kraken2Outputs],
    artifact_format=Kraken2OutputDirectoryFormat
)
plugin.register_semantic_type_to_format(
    Kraken2DB,
    artifact_format=Kraken2DBDirectoryFormat
)
plugin.register_semantic_type_to_format(
    Kraken2DBReport,
    artifact_format=Kraken2DBReportDirectoryFormat
)
plugin.register_semantic_type_to_format(
    BrackenDB,
    artifact_format=BrackenDBDirectoryFormat
)
