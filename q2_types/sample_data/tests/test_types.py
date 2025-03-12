# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest

from qiime2.plugin.testing import TestPluginBase

from q2_types.sample_data import (AlphaDiversityDirectoryFormat,
                                  SampleData, AlphaDiversity)


class TestTypes(TestPluginBase):
    package = "q2_types.sample_data.tests"

    def test_sample_data_semantic_type_registration(self):
        self.assertRegisteredSemanticType(SampleData)

    def test_alpha_diversity_semantic_type_registration(self):
        self.assertRegisteredSemanticType(AlphaDiversity)

    def test_sample_data_alpha_div_to_alpha_div_dir_fmt_registration(self):
        self.assertSemanticTypeRegisteredToFormat(
            SampleData[AlphaDiversity], AlphaDiversityDirectoryFormat)


if __name__ == '__main__':
    unittest.main()
