# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime.plugin import SemanticType

from ..plugin_setup import plugin
from . import NewickDirectoryFormat


Phylogeny = SemanticType('Phylogeny', field_names=['type'])

Rooted = SemanticType('Rooted', variant_of=Phylogeny.field['type'])

Unrooted = SemanticType('Unrooted', variant_of=Phylogeny.field['type'])

plugin.register_semantic_type(Phylogeny)
plugin.register_semantic_type(Rooted)
plugin.register_semantic_type(Unrooted)

plugin.register_semantic_type_to_format(Phylogeny[Rooted | Unrooted],
                                        artifact_format=NewickDirectoryFormat)
