# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import importlib

from .. import (OrdinationDirectoryFormat, ProcrustesStatisticsDirFmt,
                OrdinationFormat, ProcrustesStatisticsFmt,
                PCoAResults, ProcrustesStatistics)


from ...plugin_setup import plugin

plugin.register_formats(OrdinationFormat, OrdinationDirectoryFormat,
                        ProcrustesStatisticsFmt, ProcrustesStatisticsDirFmt)

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

importlib.import_module('._transformers', __name__)
