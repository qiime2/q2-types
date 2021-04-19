# ----------------------------------------------------------------------------
# Copyright (c) 2016-2021, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin import SemanticType

from ..plugin_setup import plugin
from . import OrdinationDirectoryFormat, ProcrustesStatisticsDirFmt


PCoAResults = SemanticType('PCoAResults')

ProcrustesStatistics = SemanticType('ProcrustesStatistics')

plugin.register_semantic_types(PCoAResults, ProcrustesStatistics)
plugin.register_semantic_type_to_format(
    PCoAResults,
    artifact_format=OrdinationDirectoryFormat
)

plugin.register_semantic_type_to_format(
    ProcrustesStatistics,

    artifact_format=ProcrustesStatisticsDirFmt
)
