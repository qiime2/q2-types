# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import unittest

from qiime2.plugin.testing import TestPluginBase

from q2_types.feature_map import (
    FeatureMap, MAGtoContigs, MAGtoContigsDirFmt, TaxonomyToContigs,
    FunctionToContigs, FeatureMapDirFmt
)


class TestTypes(TestPluginBase):
    package = "q2_types.feature_map.tests"

    def test_feature_map_semantic_type_registration(self):
        self.assertRegisteredSemanticType(FeatureMap)

    def test_feature_map_mag_to_contigs_semantic_type_registration(self):
        self.assertRegisteredSemanticType(MAGtoContigs)

    def test_feature_map_mag_to_contigs_fmt_registration(self):
        self.assertSemanticTypeRegisteredToFormat(
            FeatureMap[MAGtoContigs], MAGtoContigsDirFmt
        )

    def test_feature_map_taxonomy_to_contigs_semantic_type_registration(self):
        self.assertRegisteredSemanticType(TaxonomyToContigs)

    def test_feature_map_tax_annotation_to_contigs_fmt_registration(self):
        self.assertSemanticTypeRegisteredToFormat(
            FeatureMap[TaxonomyToContigs], FeatureMapDirFmt
        )

    def test_feature_map_function_to_contigs_semantic_type_registration(self):
        self.assertRegisteredSemanticType(FunctionToContigs)

    def test_feature_map_func_annotation_to_contigs_fmt_registration(self):
        self.assertSemanticTypeRegisteredToFormat(
            FeatureMap[FunctionToContigs], FeatureMapDirFmt
        )


if __name__ == "__main__":
    unittest.main()
