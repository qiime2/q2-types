# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest

import skbio

from q2_types.distance_matrix import LSMatFormat
from qiime2.plugin.testing import TestPluginBase


class TestTransformers(TestPluginBase):
    package = 'q2_types.distance_matrix.tests'

    def test_skbio_distance_matrix_to_lsmat_format(self):
        transformer = self.get_transformer(skbio.DistanceMatrix, LSMatFormat)

        filenames = ('distance-matrix-1x1.tsv', 'distance-matrix-2x2.tsv',
                     'distance-matrix-NxN.tsv')
        for filename in filenames:
            input = skbio.DistanceMatrix.read(self.get_data_path(filename))

            obs = transformer(input)
            obs = skbio.DistanceMatrix.read(str(obs))

            exp = input
            self.assertEqual(obs, exp)

    def test_lsmat_format_to_skbio_distance_matrix(self):
        filenames = ('distance-matrix-1x1.tsv', 'distance-matrix-2x2.tsv',
                     'distance-matrix-NxN.tsv')
        for filename in filenames:
            input, obs = self.transform_format(
                LSMatFormat, skbio.DistanceMatrix, filename=filename)
            exp = skbio.DistanceMatrix.read(str(input))
            self.assertEqual(obs, exp)


if __name__ == "__main__":
    unittest.main()
