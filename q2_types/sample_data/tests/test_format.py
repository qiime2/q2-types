# ----------------------------------------------------------------------------
# Copyright (c) 2016-2019, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import shutil
import unittest

from q2_types.sample_data import (AlphaDiversityDirectoryFormat,
                                  AlphaDiversityFormat)
from qiime2.plugin.testing import TestPluginBase
from qiime2.plugin import ValidationError


class TestFormats(TestPluginBase):
    package = "q2_types.sample_data.tests"

    def test_alpha_diversity_format_validate_positive(self):
        filepath = self.get_data_path('alpha-diversity.tsv')
        format = AlphaDiversityFormat(filepath, mode='r')

        format.validate()

    def test_alpha_diversity_format_validate_negative(self):
        filepath = self.get_data_path('not-alpha-diversity.tsv')
        format = AlphaDiversityFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, 'AlphaDiversityFormat'):
            format.validate()

    def test_alpha_diversity_dir_fmt_validate_positive(self):
        filepath = self.get_data_path('alpha-diversity.tsv')
        shutil.copy(filepath, self.temp_dir.name)
        format = AlphaDiversityDirectoryFormat(self.temp_dir.name, mode='r')

        format.validate()


if __name__ == '__main__':
    unittest.main()
