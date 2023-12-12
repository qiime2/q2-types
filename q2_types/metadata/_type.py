# ----------------------------------------------------------------------------
# Copyright (c) 2016-2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin import SemanticType

from ..plugin_setup import plugin
from . import ImmutableMetadataDirectoryFormat


ImmutableMetadata = SemanticType('ImmutableMetadata')

plugin.register_semantic_types(ImmutableMetadata)

plugin.register_artifact_class(
    ImmutableMetadata,
    directory_format=ImmutableMetadataDirectoryFormat,
    description=("Immutable sample or feature metadata.")
)
