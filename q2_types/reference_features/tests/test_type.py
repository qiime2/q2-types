# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest

from q2_types.reference_features import (ReferenceFeaturesDirectoryFormat,
                                         ReferenceFeatures, SSU)
from qiime2.plugin.testing import TestPluginBase


class TestTypes(TestPluginBase):
    package = "q2_types.reference_features.tests"

    def test_reference_features_semantic_type_registration(self):
        self.assertRegisteredSemanticType(ReferenceFeatures)

    def test_ssu_semantic_type_registration(self):
        self.assertRegisteredSemanticType(SSU)

    def test_ref_features_ssu_to_ref_features_dir_fmt_registration(self):
        self.assertSemanticTypeRegisteredToFormat(
            ReferenceFeatures[SSU], ReferenceFeaturesDirectoryFormat)


if __name__ == '__main__':
    unittest.main()
