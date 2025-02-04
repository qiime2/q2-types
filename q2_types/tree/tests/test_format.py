# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import shutil
import unittest

from q2_types.tree import NewickFormat, NewickDirectoryFormat
from qiime2.plugin.testing import TestPluginBase
from qiime2.plugin import ValidationError


class TestFormats(TestPluginBase):
    package = "q2_types.tree.tests"

    def test_newick_format_validate_positive(self):
        filepath = self.get_data_path('tree.nwk')
        format = NewickFormat(filepath, mode='r')

        format.validate()

    def test_newick_format_validate_negative(self):
        filepath = self.get_data_path('not-tree.nwk')
        format = NewickFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, 'NewickFormat'):
            format.validate()

    def test_newick_directory_format_validate_postivie(self):
        filepath = self.get_data_path('tree.nwk')
        shutil.copy(filepath, self.temp_dir.name)
        format = NewickDirectoryFormat(self.temp_dir.name, mode='r')

        format.validate()


if __name__ == '__main__':
    unittest.main()
