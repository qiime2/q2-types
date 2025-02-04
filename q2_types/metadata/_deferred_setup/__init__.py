# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import importlib

from .. import (ImmutableMetadataFormat, ImmutableMetadataDirectoryFormat,
                ImmutableMetadata)

from ...plugin_setup import plugin

plugin.register_formats(ImmutableMetadataFormat,
                        ImmutableMetadataDirectoryFormat)

plugin.register_semantic_types(ImmutableMetadata)

plugin.register_artifact_class(
    ImmutableMetadata,
    directory_format=ImmutableMetadataDirectoryFormat,
    description=("Immutable sample or feature metadata.")
)

importlib.import_module('._transformers', __name__)
