# ----------------------------------------------------------------------------
# Copyright (c) 2016-2023, QIIME 2 development team.
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
plugin.register_artifact_class(
    PCoAResults,
    directory_format=OrdinationDirectoryFormat,
    description="The results of running principal coordinate analysis (PCoA)."
)

plugin.register_artifact_class(
    ProcrustesStatistics,
    directory_format=ProcrustesStatisticsDirFmt,
    description="The results of running Procrustes analysis."
)
