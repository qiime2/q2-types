# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import os.path

import skbio
import skbio.io
from qiime.plugin import SemanticType, FileFormat, DataLayout

from .plugin_setup import plugin


Phylogeny = SemanticType('Phylogeny')


class NewickFormat(FileFormat):
    name = 'newick'

    @classmethod
    def sniff(cls, filepath):
        sniffer = skbio.io.io_registry.get_sniffer('newick')
        return sniffer(filepath)[0]

tree_data_layout = DataLayout('tree', 1)
tree_data_layout.register_file('tree.nwk', NewickFormat)


def tree_to_skbio_tree_node(data_dir):
    with open(os.path.join(data_dir, 'tree.nwk'), 'r') as fh:
        return skbio.TreeNode.read(fh, format='newick', verify=False)


def skbio_tree_node_to_tree(view, data_dir):
    with open(os.path.join(data_dir, 'tree.nwk'), 'w') as fh:
        view.write(fh, format='newick')


plugin.register_data_layout(tree_data_layout)

plugin.register_data_layout_reader('tree', 1, skbio.TreeNode,
                                   tree_to_skbio_tree_node)

plugin.register_data_layout_writer('tree', 1, skbio.TreeNode,
                                   skbio_tree_node_to_tree)

plugin.register_semantic_type(Phylogeny)

plugin.register_type_to_data_layout(Phylogeny, 'tree', 1)
