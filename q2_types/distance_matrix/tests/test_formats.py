# ----------------------------------------------------------------------------
# Copyright (c) 2016-2026, QIIME 2 development team.
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
from skbio.io import FileFormatError
from skbio.stats.distance import DistanceMatrixError, PairwiseMatrixError


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

        with self.assertRaises(ValidationError) as error:
            format.validate()

        self.assertIsInstance(error.exception.__cause__.__cause__,
                              FileFormatError)

    def test_lsmat_format_validate_rejects_non_symmetrical(self):
        filepath = self.get_data_path('non-symmetrical-distance-matrix.tsv')
        format = LSMatFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, 'symmetric') as error:
            format.validate()

        self.assertIsInstance(error.exception.__cause__.__cause__,
                              DistanceMatrixError)

    def test_lsmat_format_validate_rejects_nonzero_diagonal(self):
        filepath = self.get_data_path('nonzero-diagonal-distance-matrix.tsv')
        format = LSMatFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, 'hollow') as error:
            format.validate()

        self.assertIsInstance(error.exception.__cause__.__cause__,
                              DistanceMatrixError)

    def test_lsmat_format_validate_rejects_non_numeric_value(self):
        filepath = self.get_data_path('non-numeric-distance-matrix.tsv')
        format = LSMatFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError,
                                    'could not be read') as error:
            format.validate()

        self.assertIsInstance(error.exception.__cause__.__cause__, ValueError)

    def test_lsmat_format_validate_rejects_duplicate_ids(self):
        filepath = self.get_data_path('duplicate-ids-distance-matrix.tsv')
        format = LSMatFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError,
                                    'IDs must be unique') as error:
            format.validate()

        self.assertIsInstance(error.exception.__cause__.__cause__,
                              PairwiseMatrixError)

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
