# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import os
import shutil
import unittest

from qiime2.plugin.testing import TestPluginBase
from qiime2.plugin import ValidationError

from q2_types.ordination import (
    OrdinationFormat, OrdinationDirectoryFormat,
    ProcrustesStatisticsFmt, ProcrustesStatisticsDirFmt)


class TestFormats(TestPluginBase):
    package = 'q2_types.ordination.tests'

    def test_ordination_format_validate_positive(self):
        filepath = self.get_data_path('pcoa-results-NxN.txt')
        format = OrdinationFormat(filepath, mode='r')

        format.validate()

    def test_ordination_format_validate_negative(self):
        filepath = self.get_data_path('not-pcoa-results.txt')
        format = OrdinationFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, 'OrdinationFormat'):
            format.validate()

    def test_ordination_dir_format_validate_positive(self):
        filepath = self.get_data_path('pcoa-results-NxN.txt')
        shutil.copy(filepath,
                    os.path.join(self.temp_dir.name, 'ordination.txt'))
        format = OrdinationDirectoryFormat(self.temp_dir.name, mode='r')

        format.validate()

    def test_m2_stats_fmt_positive(self):
        filepath = self.get_data_path('m2stats-999-permus.tsv')
        format = ProcrustesStatisticsFmt(filepath, mode='r')

        format.validate(level='max')

        # If we made it this far, congrats!
        self.assertTrue(True)

    def test_m2_stats_dir_fmt_positive(self):
        filepath = self.get_data_path('m2stats-999-permus.tsv')
        shutil.copy(filepath,
                    os.path.join(self.temp_dir.name,
                                 'ProcrustesStatistics.tsv'))
        format = ProcrustesStatisticsDirFmt(self.temp_dir.name, mode='r')

        format.validate(level='max')

        # If we made it this far, congrats!
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
