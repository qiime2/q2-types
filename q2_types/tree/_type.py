# ----------------------------------------------------------------------------
# Copyright (c) 2016-2022, QIIME 2 development team.
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

plugin.register_artifact_class(
    Phylogeny[Rooted], NewickDirectoryFormat,
    "A phylogenetic tree containing a defined root.")

plugin.register_artifact_class(
    Phylogeny[Unrooted], NewickDirectoryFormat,
    "A phylogenetic tree not containing a defined root.")

plugin.register_semantic_type_to_format(Hierarchy,
                                        directory_format=NewickDirectoryFormat)
