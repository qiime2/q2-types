# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import os.path
import shutil
import unittest

from q2_types.distance_matrix import LSMatFormat, DistanceMatrixDirectoryFormat
from qiime2.plugin.testing import TestPluginBase
from qiime2.plugin import ValidationError


class TestFormats(TestPluginBase):
    package = 'q2_types.distance_matrix.tests'

    def test_lsmat_format_validate_positive(self):
        filenames = ('distance-matrix-1x1.tsv', 'distance-matrix-2x2.tsv',
                     'distance-matrix-NxN.tsv')
        for filename in filenames:
            filepath = self.get_data_path(filename)
            format = LSMatFormat(filepath, mode='r')

            # Should not error.
            format.validate()

    def test_lsmat_format_validate_negative(self):
        filepath = self.get_data_path('not-lsmat')
        format = LSMatFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, 'LSMat'):
            format.validate()

    def test_distance_matrix_directory_format(self):
        # This test exists mainly to assert that the single-file directory
        # format is defined and functional. More extensive testing is performed
        # on its underlying format (LSMatFormat).
        filepath = self.get_data_path('distance-matrix-NxN.tsv')
        shutil.copy(filepath,
                    os.path.join(self.temp_dir.name, 'distance-matrix.tsv'))
        format = DistanceMatrixDirectoryFormat(self.temp_dir.name, mode='r')

        # Should not error.
        format.validate()


if __name__ == "__main__":
    unittest.main()
