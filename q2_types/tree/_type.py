# ----------------------------------------------------------------------------
# Copyright (c) 2016-2021, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin import SemanticType

from ..plugin_setup import plugin
from . import NewickDirectoryFormat


Phylogeny = SemanticType('Phylogeny', field_names=['type'])

Rooted = SemanticType('Rooted', variant_of=Phylogeny.field['type'])

Unrooted = SemanticType('Unrooted', variant_of=Phylogeny.field['type'])

Hierarchy = SemanticType('Hierarchy')

plugin.register_semantic_types(Phylogeny, Rooted, Unrooted, Hierarchy)

plugin.register_semantic_type_to_format(Phylogeny[Rooted | Unrooted],
                                        artifact_format=NewickDirectoryFormat)

plugin.register_semantic_type_to_format(Hierarchy,
                                        artifact_format=NewickDirectoryFormat)
