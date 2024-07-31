# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import importlib

from q2_types.sample_data import SampleData
from q2_types.feature_data import FeatureData

from .. import (
    Kraken2ReportFormat, Kraken2ReportDirectoryFormat,
    Kraken2OutputFormat, Kraken2OutputDirectoryFormat,
    Kraken2DBFormat, Kraken2DBReportFormat, Kraken2DBReportDirectoryFormat,
    Kraken2DBDirectoryFormat, BrackenDBFormat, BrackenDBDirectoryFormat,
    Kraken2Reports, Kraken2Outputs, Kraken2DB, Kraken2DBReport, BrackenDB)

from ...plugin_setup import plugin


plugin.register_formats(
    Kraken2ReportFormat, Kraken2OutputFormat,
    Kraken2DBFormat, Kraken2DBReportFormat,
    Kraken2ReportDirectoryFormat, Kraken2OutputDirectoryFormat,
    Kraken2DBDirectoryFormat, Kraken2DBReportDirectoryFormat,
    BrackenDBFormat, BrackenDBDirectoryFormat
)

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

importlib.import_module('._transformers', __name__)
