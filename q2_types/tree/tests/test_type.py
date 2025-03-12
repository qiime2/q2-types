# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest

from q2_types.tree import (Phylogeny, Rooted, Unrooted,
                           Hierarchy, NewickDirectoryFormat)
from qiime2.plugin.testing import TestPluginBase


class TestTypes(TestPluginBase):
    package = "q2_types.tree.tests"

    def test_phylogeny_semantic_type_registration(self):
        self.assertRegisteredSemanticType(Phylogeny)

    def test_rooted_semantic_type_registration(self):
        self.assertRegisteredSemanticType(Rooted)

    def test_unrooted_semantic_type_registration(self):
        self.assertRegisteredSemanticType(Unrooted)

    def test_hierarchy_semantic_type_registration(self):
        self.assertRegisteredSemanticType(Hierarchy)

    def test_phylogeny_rooted_unrooted_to_newick_dir_fmt_registration(self):
        self.assertSemanticTypeRegisteredToFormat(
            Phylogeny[Rooted], NewickDirectoryFormat)
        self.assertSemanticTypeRegisteredToFormat(
            Phylogeny[Unrooted], NewickDirectoryFormat)

    def test_hierarchy_to_newick_dir_fmt_registration(self):
        self.assertSemanticTypeRegisteredToFormat(
            Hierarchy, NewickDirectoryFormat)


if __name__ == '__main__':
    unittest.main()
