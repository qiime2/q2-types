# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from .. import KaijuIndexFormat, KaijuDBDirectoryFormat, KaijuDB

from ...plugin_setup import plugin

plugin.register_formats(KaijuDBDirectoryFormat, KaijuIndexFormat)

plugin.register_semantic_types(KaijuDB)

plugin.register_semantic_type_to_format(
    KaijuDB, artifact_format=KaijuDBDirectoryFormat
)
