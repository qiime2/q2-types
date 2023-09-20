# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import unittest

from qiime2.plugin.testing import TestPluginBase

from .._type import (FeatureMap, MAGtoContigs)
from .._format import MAGtoContigsDirFmt


class TestTypes(TestPluginBase):
    package = "q2_types.feature_map.tests"

    def test_feature_map_semantic_type_registration(self):
        self.assertRegisteredSemanticType(FeatureMap)

    def test_feature_map_mag_to_contigs_semantic_type_registration(self):
        self.assertRegisteredSemanticType(MAGtoContigs)

    def test_feature_map_to_dir_fmt_registration(self):
        self.assertSemanticTypeRegisteredToFormat(
            FeatureMap[MAGtoContigs], MAGtoContigsDirFmt
        )


if __name__ == "__main__":
    unittest.main()
