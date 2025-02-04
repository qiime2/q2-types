# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest

from q2_types.distance_matrix import (DistanceMatrix,
                                      DistanceMatrixDirectoryFormat)
from qiime2.plugin.testing import TestPluginBase


class TestTypes(TestPluginBase):
    package = 'q2_types.distance_matrix.tests'

    def test_distance_matrix_semantic_type_registration(self):
        self.assertRegisteredSemanticType(DistanceMatrix)

    def test_distance_matrix_semantic_type_to_format_registration(self):
        self.assertSemanticTypeRegisteredToFormat(
            DistanceMatrix, DistanceMatrixDirectoryFormat)


if __name__ == "__main__":
    unittest.main()
