# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest

import skbio

from q2_types.tree import NewickFormat
from qiime2.plugin.testing import TestPluginBase


class TestTransformers(TestPluginBase):
    package = "q2_types.tree.tests"

    def test_skbio_tree_node_to_newick_format(self):
        filepath = self.get_data_path('tree.nwk')
        transformer = self.get_transformer(skbio.TreeNode, NewickFormat)
        input = skbio.TreeNode.read(filepath)

        obs = transformer(input)
        obs = skbio.TreeNode.read(str(obs))

        self.assertEqual(str(input), str(obs))

    def test_newick_format_to_skbio_tree_node(self):
        filename = 'tree.nwk'
        input, obs = self.transform_format(NewickFormat, skbio.TreeNode,
                                           filename)

        exp = skbio.TreeNode.read(str(input))

        self.assertEqual(str(exp), str(obs))


if __name__ == '__main__':
    unittest.main()
