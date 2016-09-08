# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest

from q2_types.plugin_setup import plugin
from q2_types.distance_matrix import (DistanceMatrix,
                                      DistanceMatrixDirectoryFormat)
from q2_types.testing import TestPluginBase


class TestTypes(TestPluginBase):
    def test_distance_matrix_semantic_type_registration(self):
        self.assertEqual(plugin.types['DistanceMatrix'].semantic_type,
                         DistanceMatrix)

    def test_distance_matrix_semantic_type_to_format_registration(self):
        format = None
        for type_format_record in plugin.type_formats:
            if type_format_record.type_expression == DistanceMatrix:
                format = type_format_record.format
                break

        self.assertIsNotNone(format)
        self.assertEqual(format, DistanceMatrixDirectoryFormat)


if __name__ == "__main__":
    unittest.main()
