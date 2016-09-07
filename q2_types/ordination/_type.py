# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime.plugin import SemanticType

from ..plugin_setup import plugin
from ._format import OrdinationDirectoryFormat


PCoAResults = SemanticType('PCoAResults')

plugin.register_semantic_type(PCoAResults)
plugin.register_semantic_type_to_format(
    PCoAResults,
    artifact_format=OrdinationDirectoryFormat
)
