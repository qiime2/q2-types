# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest

from q2_types.feature_data import FeatureData
from qiime2.plugin.testing import TestPluginBase

from q2_types.feature_data_mag import (
        MAG, MAGSequencesDirFmt, OrthologAnnotationDirFmt, NOG, OG, KEGG,
        )


class TestTypes(TestPluginBase):
    package = 'q2_types.feature_data_mag.tests'

    def test_mag_semantic_type_registration(self):
        self.assertRegisteredSemanticType(MAG)

    def test_mags_semantic_type_to_format_registration(self):
        self.assertSemanticTypeRegisteredToFormat(
            FeatureData[MAG],
            MAGSequencesDirFmt
        )

    def test_nog_type_registration(self):
        self.assertRegisteredSemanticType(NOG)

    def test_og_type_registration(self):
        self.assertRegisteredSemanticType(OG)

    def test_kegg_type_registration(self):
        self.assertRegisteredSemanticType(KEGG)

    def test_nog_registered_to_format(self):
        self.assertSemanticTypeRegisteredToFormat(
                FeatureData[NOG],
                OrthologAnnotationDirFmt)

    def test_og_registered_to_format(self):
        self.assertSemanticTypeRegisteredToFormat(
                FeatureData[OG],
                OrthologAnnotationDirFmt)

    def test_kegg_registered_to_format(self):
        self.assertSemanticTypeRegisteredToFormat(
                FeatureData[KEGG],
                OrthologAnnotationDirFmt)


if __name__ == '__main__':
    unittest.main()
