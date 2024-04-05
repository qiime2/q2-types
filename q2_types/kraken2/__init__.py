# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import importlib

from ._format import (
    Kraken2ReportFormat, Kraken2ReportDirectoryFormat,
    Kraken2OutputFormat, Kraken2OutputDirectoryFormat,
    Kraken2DBFormat, Kraken2DBReportFormat, Kraken2DBReportDirectoryFormat,
    Kraken2DBDirectoryFormat, BrackenDBFormat, BrackenDBDirectoryFormat
)
from ._type import Kraken2Reports, Kraken2Outputs, Kraken2DB, Kraken2DBReport

__all__ = [
    'Kraken2ReportFormat', 'Kraken2ReportDirectoryFormat', 'Kraken2Reports',
    'Kraken2OutputFormat', 'Kraken2OutputDirectoryFormat', 'Kraken2Outputs',
    'Kraken2DBFormat', 'Kraken2DBReportFormat', 'Kraken2DBReport',
    'Kraken2DBReportDirectoryFormat', 'Kraken2DBDirectoryFormat', 'Kraken2DB',
    'BrackenDBFormat', 'BrackenDBDirectoryFormat'
]

importlib.import_module('q2_types.kraken2._format')
importlib.import_module('q2_types.kraken2._transformer')
importlib.import_module('q2_types.kraken2._type')
