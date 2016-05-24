# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import os.path

import skbio
from qiime.plugin import SemanticType

from .plugin_setup import plugin


Phylogeny = SemanticType('Phylogeny')


def validator(data_dir):
    raise NotImplementedError()


def tree_to_skbio_tree_node(data_dir):
    with open(os.path.join(data_dir, 'tree.nwk'), 'r') as fh:
        return skbio.TreeNode.read(fh, format='newick', verify=False)


def skbio_tree_node_to_tree(view, data_dir):
    with open(os.path.join(data_dir, 'tree.nwk'), 'w') as fh:
        view.write(fh, format='newick')


plugin.register_archive_format('tree', 1, validator)

plugin.register_archive_format_reader('tree', 1,
                                      skbio.TreeNode,
                                      tree_to_skbio_tree_node)

plugin.register_archive_format_writer('tree', 1,
                                      skbio.TreeNode,
                                      skbio_tree_node_to_tree)

plugin.register_semantic_type(Phylogeny)

plugin.register_type_to_archive_format(Phylogeny, 'tree', 1)
