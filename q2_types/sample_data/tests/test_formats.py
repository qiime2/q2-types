# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import shutil
import unittest

from qiime2.plugin.testing import TestPluginBase
from qiime2.plugin import ValidationError

from q2_types.sample_data import (AlphaDiversityDirectoryFormat,
                                  AlphaDiversityFormat)


class TestFormats(TestPluginBase):
    package = "q2_types.sample_data.tests"

    def test_alpha_diversity_format_validate_positive(self):
        filepath = self.get_data_path('alpha-diversity.tsv')
        format = AlphaDiversityFormat(filepath, mode='r')

        # Should succeed
        format.validate()

    def test_alpha_diversity_dir_fmt_validate_positive(self):
        filepath = self.get_data_path('alpha-diversity.tsv')
        shutil.copy(filepath, self.temp_dir.name)
        format = AlphaDiversityDirectoryFormat(self.temp_dir.name, mode='r')

        # Should succeed
        format.validate()

    def test_alpha_diversity_format_validate_positive_one_sample(self):
        filepath = self.get_data_path('alpha-diversity-one-sample.tsv')
        format = AlphaDiversityFormat(filepath, mode='r')

        # Should succeed
        format.validate()

    def test_alpha_diversity_format_validate_positive_md_columns(self):
        filepath = self.get_data_path('alpha-diversity-with-metadata.tsv')
        format = AlphaDiversityFormat(filepath, mode='r')

        # Should succeed
        format.validate()

    def test_alpha_diversity_format_validate_negative_no_records(self):
        filepath = self.get_data_path('alpha-diversity-missing-records.tsv')
        format = AlphaDiversityFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, 'No records found'):
            format.validate()

    def test_alpha_diversity_format_validate_negative_too_few_cols(self):
        filepath = self.get_data_path('alpha-diversity-one-column.tsv')
        format = AlphaDiversityFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, 'line 1.*2 columns'):
            format.validate()

    def test_alpha_diversity_format_validate_negative_jagged_rows(self):
        filepath = self.get_data_path('alpha-diversity-jagged-rows.tsv')
        format = AlphaDiversityFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, 'Line 3.*expected 3'):
            format.validate()


if __name__ == '__main__':
    unittest.main()
