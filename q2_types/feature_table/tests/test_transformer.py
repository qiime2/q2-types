# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest

import biom
import pandas as pd

from q2_types.feature_table import BIOMV100Format, BIOMV210Format
from qiime.plugin.testing import TestPluginBase


class TestTransformers(TestPluginBase):
    package = 'q2_types.feature_table.tests'

    def test_biom_table_to_biom_v100_format(self):
        filepath = self.get_data_path('feature-table_v100.biom')
        transformer = self.get_transformer(biom.Table, BIOMV100Format)
        input = biom.load_table(filepath)

        obs = transformer(input)
        obs = biom.load_table(str(obs))

        exp = input
        self.assertEqual(obs.ids(axis='observation').all(),
                         exp.ids(axis='observation').all())
        self.assertEqual(obs.ids(axis='sample').all(),
                         exp.ids(axis='sample').all())

    def test_biom_v100_format_to_biom_table(self):
        filepath = self.get_data_path('feature-table_v100.biom')
        transformer = self.get_transformer(BIOMV100Format, biom.Table)
        input = BIOMV100Format(filepath, mode='r')

        obs = transformer(input)

        exp = biom.load_table(filepath)
        self.assertEqual(obs.ids(axis='observation').all(),
                         exp.ids(axis='observation').all())
        self.assertEqual(obs.ids(axis='sample').all(),
                         exp.ids(axis='sample').all())

    def test_biom_v100_format_to_pandas_data_frame(self):
        filepath = self.get_data_path('feature-table_v100.biom')
        transformer = self.get_transformer(BIOMV100Format, pd.DataFrame)
        input = BIOMV100Format(filepath, mode='r')

        obs = transformer(input)

        self.assertIsInstance(obs, pd.DataFrame)

    def test_biom_v210_format_to_pandas_data_frame(self):
        filepath = self.get_data_path('feature-table_v210.biom')
        transformer = self.get_transformer(BIOMV210Format, pd.DataFrame)
        input = BIOMV210Format(filepath, mode='r')

        obs = transformer(input)

        self.assertIsInstance(obs, pd.DataFrame)

    def test_biom_v210_format_to_biom_table(self):
        filepath = self.get_data_path('feature-table_v210.biom')
        transformer = self.get_transformer(BIOMV210Format, biom.Table)
        input = BIOMV210Format(filepath, mode='r')

        obs = transformer(input)

        self.assertIsInstance(obs, biom.Table)

    def test_biom_table_to_biom_v210_format(self):
        filepath = self.get_data_path('feature-table_v210.biom')
        transformer = self.get_transformer(biom.Table, BIOMV210Format)
        input = biom.load_table(filepath)

        obs = transformer(input)
        obs = biom.load_table(str(obs))

        exp = input
        self.assertEqual(obs.ids(axis='observation').all(),
                         exp.ids(axis='observation').all())
        self.assertEqual(obs.ids(axis='sample').all(),
                         exp.ids(axis='sample').all())

    def test_biom_table_to_pandas_data_frame(self):
        filepath = self.get_data_path('feature-table_v100.biom')
        transformer = self.get_transformer(biom.Table, pd.DataFrame)
        input = biom.load_table(filepath)

        obs = transformer(input)

        self.assertIsInstance(obs, pd.DataFrame)

    def test_biom_v100_format_to_biom_v210_format(self):
        filepath = self.get_data_path('feature-table_v100.biom')
        transformer = self.get_transformer(BIOMV100Format, BIOMV210Format)
        input = BIOMV100Format(filepath, mode='r')

        obs = transformer(input)

        self.assertIsInstance(obs, BIOMV210Format)

if __name__ == "__main__":
    unittest.main()
