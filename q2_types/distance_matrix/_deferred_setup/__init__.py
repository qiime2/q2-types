# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import importlib

from .. import LSMatFormat, DistanceMatrixDirectoryFormat
from .. import DistanceMatrix

from ...plugin_setup import plugin

plugin.register_formats(LSMatFormat, DistanceMatrixDirectoryFormat)

plugin.register_semantic_types(DistanceMatrix)

plugin.register_artifact_class(
    DistanceMatrix,
    directory_format=DistanceMatrixDirectoryFormat,
    description="A symmetric matrix representing distances between entities."
)

importlib.import_module('._transformers', __name__)
