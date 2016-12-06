# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import shutil
import unittest

from q2_types.reference_features import ReferenceFeaturesDirectoryFormat
from qiime.plugin.testing import TestPluginBase


class TestFormats(TestPluginBase):
    package = "q2_types.reference_features.tests"

    def test_reference_features_dir_fmt_validate_positive(self):
        filenames = ('dna-sequences.fasta', 'aligned-dna-sequences.fasta',
                     'taxonomy.tsv', 'tree.nwk')
        for filename in filenames:
            shutil.copy(self.get_data_path(filename), self.temp_dir.name)

        format = ReferenceFeaturesDirectoryFormat(self.temp_dir.name, mode='r')

        format.validate()

    def test_reference_features_dir_fmt_validate_negative(self):
        pass


if __name__ == '__main__':
    unittest.main()
