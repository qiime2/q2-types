# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import importlib
from io import StringIO

from skbio import TreeNode

from qiime2.plugin.util import transform

from .. import (NewickFormat, NewickDirectoryFormat,
                Phylogeny, Rooted, Unrooted, Hierarchy)

from ...plugin_setup import plugin

plugin.register_formats(NewickFormat, NewickDirectoryFormat)

plugin.register_semantic_types(Phylogeny, Rooted, Unrooted, Hierarchy)

plugin.register_artifact_class(
    Phylogeny[Unrooted], NewickDirectoryFormat,
    "A phylogenetic tree not containing a defined root.")


# Phylogeny[Rooted] import usage example
def phylogeny_rooted_usage(use):
    def factory():
        from q2_types.tree import NewickFormat

        tree = TreeNode.read(StringIO(
            '(SEQUENCE1:0.000000003,SEQUENCE2:0.000000003);'))
        ff = transform(tree, to_type=NewickFormat)
        ff.validate()
        return ff

    to_import = use.init_format('my-tree', factory, ext='.tre')

    use.import_from_format('tree',
                           semantic_type='Phylogeny[Rooted]',
                           variable=to_import,
                           view_type='NewickFormat')


plugin.register_artifact_class(
    Phylogeny[Rooted], NewickDirectoryFormat,
    "A phylogenetic tree containing a defined root.",
    examples={'Import rooted phylogenetic tree': phylogeny_rooted_usage})

plugin.register_artifact_class(Hierarchy,
                               directory_format=NewickDirectoryFormat)

importlib.import_module('._transformers', __name__)
