# ----------------------------------------------------------------------------
# Copyright (c) 2016-2026, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest

import skbio
import pandas as pd

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

    def test_lsmat_format_to_pd_series(self):
        filenames = ('distance-matrix-2x2.tsv',
                     'distance-matrix-NxN.tsv')
        for filename in filenames:
            input, obs = self.transform_format(LSMatFormat,
                                               pd.Series,
                                               filename=filename)
            exp = skbio.DistanceMatrix.read(str(input)).to_series()
        pd.testing.assert_series_equal(obs, exp)

    def test_lsmat_format_to_pd_series_1x1(self):
        filename = 'distance-matrix-1x1.tsv'
        with self.assertRaisesRegex(AssertionError, "Distance Matrix *"):
            self.transform_format(LSMatFormat,
                                  pd.Series,
                                  filename=filename)

    def test_pd_series_to_skbio_distance_matrix(self):
        transformer = self.get_transformer(pd.Series, LSMatFormat)

        filenames = ('distance-matrix-NxN.tsv', 'distance-matrix-2x2.tsv')
        for filename in filenames:
            input = skbio.DistanceMatrix.read(self.get_data_path(filename))
            obs = transformer(input.to_series())
            obs = skbio.DistanceMatrix.read(str(obs))

            exp = input

            self.assertEqual(obs, exp)

    def test_lsmat_format_to_pd_data_frame(self):
        filenames = ('distance-matrix-1x1.tsv', 'distance-matrix-2x2.tsv',
                     'distance-matrix-NxN.tsv')
        for filename in filenames:
            input, obs = self.transform_format(LSMatFormat,
                                               pd.DataFrame,
                                               filename=filename)
            exp = skbio.DistanceMatrix.read(str(input)).to_data_frame()
            pd.testing.assert_frame_equal(obs, exp)

    def test_pd_data_frame_to_skbio_distance_matrix(self):
        transformer = self.get_transformer(pd.DataFrame, LSMatFormat)

        filenames = ('distance-matrix-1x1.tsv', 'distance-matrix-2x2.tsv',
                     'distance-matrix-NxN.tsv')
        for filename in filenames:
            input = skbio.DistanceMatrix.read(self.get_data_path(filename))
            obs = transformer(input.to_data_frame())
            obs = skbio.DistanceMatrix.read(str(obs))
            exp = input
            self.assertEqual(obs, exp)

    def test_pd_data_frame_to_lsmat_format_rejects_misordered_columns(self):
        transformer = self.get_transformer(pd.DataFrame, LSMatFormat)
        dm = skbio.DistanceMatrix.read(
            self.get_data_path('distance-matrix-NxN.tsv'))
        data = dm.to_data_frame().reindex(columns=dm.ids[::-1])

        with self.assertRaisesRegex(
                ValueError, "same IDs in the same order"):
            transformer(data)


if __name__ == "__main__":
    unittest.main()
