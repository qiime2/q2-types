# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import os
import shutil

from q2_types.ordination import OrdinationFormat, OrdinationDirectoryFormat
from qiime.plugin.testing import TestPluginBase


class TestFormats(TestPluginBase):
    package = 'q2_types.ordination.tests'

    def test_ordination_format_validate_positive(self):
        filepath = self.get_data_path('pcoa-results.txt')
        format = OrdinationFormat(filepath, mode='r')

        format.validate()

    def test_ordination_format_validate_negative(self):
        filepath = self.get_data_path('not-pcoa-results.txt')
        format = OrdinationFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValueError, 'OrdinationFormat'):
            format.validate()

    def test_ordination_dir_format_validate_positive(self):
        filepath = self.get_data_path('pcoa-results.txt')
        shutil.copy(filepath,
                    os.path.join(self.temp_dir.name, 'ordination.txt'))
        format = OrdinationDirectoryFormat(self.temp_dir.name, mode='r')

        format.validate()
