# ----------------------------------------------------------------------------
# Copyright (c) 2016-2022, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin import SemanticType

from ..plugin_setup import plugin
from . import DistanceMatrixDirectoryFormat


DistanceMatrix = SemanticType('DistanceMatrix')

plugin.register_semantic_types(DistanceMatrix)
plugin.register_artifact_class(
    DistanceMatrix,
    directory_format=DistanceMatrixDirectoryFormat
)
