# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
from qiime2.plugin import SemanticType

from . import KaijuDBDirectoryFormat
from ..plugin_setup import plugin


KaijuDB = SemanticType("KaijuDB")

plugin.register_semantic_types(KaijuDB)

plugin.register_semantic_type_to_format(
    KaijuDB, artifact_format=KaijuDBDirectoryFormat
)
