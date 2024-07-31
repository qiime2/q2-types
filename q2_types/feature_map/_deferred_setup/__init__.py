# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import importlib

from .. import MAGtoContigs, FeatureMap, MAGtoContigsDirFmt, MAGtoContigsFormat

from ...plugin_setup import plugin

plugin.register_formats(MAGtoContigsFormat, MAGtoContigsDirFmt)

plugin.register_semantic_types(FeatureMap, MAGtoContigs)

plugin.register_artifact_class(
    FeatureMap[MAGtoContigs],
    directory_format=MAGtoContigsDirFmt
)

importlib.import_module('._transformers', __name__)
