# ----------------------------------------------------------------------------
# Copyright (c) 2016-2021, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin import SemanticType

from ..plugin_setup import plugin
from . import OrdinationDirectoryFormat, ProcrustesM2StatDFmt


PCoAResults = SemanticType('PCoAResults')

ProcrustesM2Statistic = SemanticType('ProcrustesM2Statistic')

plugin.register_semantic_types(PCoAResults, ProcrustesM2Statistic)
plugin.register_semantic_type_to_format(
    PCoAResults,
    artifact_format=OrdinationDirectoryFormat
)

plugin.register_semantic_type_to_format(
    ProcrustesM2Statistic,
    artifact_format=ProcrustesM2StatDFmt
)
