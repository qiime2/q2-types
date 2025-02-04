# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest

import biom
import pandas as pd
from numpy.testing import assert_array_equal
from pandas.testing import assert_frame_equal

import qiime2
from qiime2.plugin.testing import TestPluginBase

from q2_types.feature_table import BIOMV100Format, BIOMV210Format
from q2_types.feature_table._deferred_setup._transformers import (
    _parse_biom_table_v100, _parse_biom_table_v210, _table_to_dataframe,
    _table_to_metadata)


class TestTransformers(TestPluginBase):
    package = 'q2_types.feature_table.tests'

    def test_biom_v100_format_to_biom_table(self):
        input, obs = self.transform_format(BIOMV100Format, biom.Table,
                                           filename='feature-table_v100.biom')

        exp = biom.load_table(str(input))
        assert_array_equal(obs.ids(axis='observation'),
                           exp.ids(axis='observation'))
        assert_array_equal(obs.ids(axis='sample'), exp.ids(axis='sample'))

    def test_biom_v100_format_to_pandas_data_frame(self):
        input, obs = self.transform_format(BIOMV100Format, pd.DataFrame,
                                           filename='feature-table_v100.biom')

        table = _parse_biom_table_v100(input)
        df = _table_to_dataframe(table)

        assert_frame_equal(df, obs)

    def test_biom_v210_format_to_pandas_data_frame(self):
        input, obs = self.transform_format(BIOMV210Format, pd.DataFrame,
                                           filename='feature-table_v210.biom')

        table = _parse_biom_table_v210(input)
        df = _table_to_dataframe(table)

        assert_frame_equal(df, obs)

    def test_biom_v210_format_to_biom_table(self):
        input, obs = self.transform_format(BIOMV210Format, biom.Table,
                                           filename='feature-table_v210.biom')

        exp = biom.load_table(str(input))

        assert_array_equal(obs.ids(axis='observation'),
                           exp.ids(axis='observation'))
        assert_array_equal(obs.ids(axis='sample'), exp.ids(axis='sample'))

    def test_biom_table_to_biom_v210_format(self):
        filepath = self.get_data_path('feature-table_v210.biom')
        transformer = self.get_transformer(biom.Table, BIOMV210Format)
        input = biom.load_table(filepath)

        obs = transformer(input)
        obs = biom.load_table(str(obs))

        exp = input
        assert_array_equal(obs.ids(axis='observation'),
                           exp.ids(axis='observation'))
        assert_array_equal(obs.ids(axis='sample'), exp.ids(axis='sample'))

    def test_biom_table_to_pandas_data_frame(self):
        filepath = self.get_data_path('feature-table_v100.biom')
        transformer = self.get_transformer(biom.Table, pd.DataFrame)
        input = biom.load_table(filepath)

        obs = transformer(input)

        self.assertIsInstance(obs, pd.DataFrame)

    def test_biom_v100_format_to_biom_v210_format(self):
        input, obs = self.transform_format(BIOMV100Format, BIOMV210Format,
                                           filename='feature-table_v100.biom')
        exp = biom.load_table(str(input))
        obs = biom.load_table(str(obs))

        assert_array_equal(obs.ids(axis='observation'),
                           exp.ids(axis='observation'))
        assert_array_equal(obs.ids(axis='sample'), exp.ids(axis='sample'))

    def test_to_pandas_data_frame_to_biom_v210_format(self):
        filepath = self.get_data_path('feature-table_v100.biom')
        transformer1 = self.get_transformer(BIOMV100Format, pd.DataFrame)
        input = BIOMV100Format(filepath, mode='r')
        df = transformer1(input)

        transformer2 = self.get_transformer(pd.DataFrame, BIOMV210Format)
        obs = transformer2(df)
        self.assertIsInstance(obs, BIOMV210Format)

    def test_to_pandas_dataframe_bad_index(self):
        transformer = self.get_transformer(pd.DataFrame, BIOMV210Format)
        df = pd.DataFrame([[1, 2], [2, 3]], columns=['ATG', 'ACG'])
        with self.assertRaisesRegex(TypeError, 'string-based'):
            transformer(df)

        df = pd.DataFrame([[1, 2], [2, 3]], columns=['ATG', 'ACG'],
                          index=[98, 99])
        with self.assertRaisesRegex(TypeError, 'string-based'):
            transformer(df)

    def test_to_pandas_data_frame_to_biom_table(self):
        filepath = self.get_data_path('feature-table_v100.biom')
        transformer1 = self.get_transformer(BIOMV100Format, pd.DataFrame)
        input = BIOMV100Format(filepath, mode='r')
        df = transformer1(input)

        transformer2 = self.get_transformer(pd.DataFrame, biom.Table)
        obs = transformer2(df)
        self.assertIsInstance(obs, biom.Table)

    def test_biom_table_to_metadata(self):
        filepath = self.get_data_path('feature-table_v100.biom')
        transformer = self.get_transformer(biom.Table, qiime2.Metadata)
        input = biom.load_table(filepath)

        obs = transformer(input)

        self.assertIsInstance(obs, qiime2.Metadata)

    def test_biom_v100_format_to_metadata(self):
        input, obs = self.transform_format(BIOMV100Format, qiime2.Metadata,
                                           filename='feature-table_v100.biom')

        table = _parse_biom_table_v100(input)
        df = _table_to_metadata(table)

        self.assertEqual(df, obs)

    def test_biom_v210_format_to_metadata(self):
        input, obs = self.transform_format(BIOMV210Format, qiime2.Metadata,
                                           filename='feature-table_v210.biom')

        table = _parse_biom_table_v210(input)
        df = _table_to_metadata(table)

        self.assertEqual(df, obs)


if __name__ == "__main__":
    unittest.main()
