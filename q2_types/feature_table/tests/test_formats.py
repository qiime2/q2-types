# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import shutil
import os
import unittest

from q2_types.feature_table import (BIOMV100Format, BIOMV210Format,
                                    BIOMV100DirFmt, BIOMV210DirFmt)
from qiime2.plugin.testing import TestPluginBase
from qiime2.plugin import ValidationError


class TestFormats(TestPluginBase):
    package = 'q2_types.feature_table.tests'

    def test_biomv100_format_validate_positive(self):
        filepath = self.get_data_path('feature-table_v100.biom')
        format = BIOMV100Format(filepath, mode='r')

        format.validate()

    def test_biomv100_format_validate_negative(self):
        filepath = self.get_data_path('feature-table_v210.biom')
        format = BIOMV100Format(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, 'BIOMV100Format'):
            format.validate()

    def test_biomv210_format_validate_positive(self):
        filepath = self.get_data_path('feature-table_v210.biom')
        format = BIOMV210Format(filepath, mode='r')

        format.validate()

    def test_biomv210_format_validate_negative(self):
        filepath = self.get_data_path('feature-table_v100.biom')
        format = BIOMV210Format(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, 'BIOMV210Format'):
            format.validate()

    def test_biomv100_dir_format_validate_positive(self):
        filepath = self.get_data_path('feature-table_v100.biom')
        shutil.copy(filepath,
                    os.path.join(self.temp_dir.name, 'feature-table.biom'))
        format = BIOMV100DirFmt(self.temp_dir.name, mode='r')

        format.validate()

    def test_biomv210_dir_format_validate_positive(self):
        filepath = self.get_data_path('feature-table_v210.biom')
        shutil.copy(filepath,
                    os.path.join(self.temp_dir.name, 'feature-table.biom'))
        format = BIOMV210DirFmt(self.temp_dir.name, mode='r')

        format.validate()


if __name__ == "__main__":
    unittest.main()
