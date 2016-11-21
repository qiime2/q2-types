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
import numpy as np

from q2_types.feature_table import BIOMV100Format, BIOMV210Format
from q2_types.feature_data import TaxonomyFormat
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

    def test_to_pandas_data_frame_to_biom_v210_format(self):
        # load a table to a pd.DataFrame
        filepath = self.get_data_path('feature-table_v100.biom')
        transformer1 = self.get_transformer(BIOMV100Format, pd.DataFrame)
        input = BIOMV100Format(filepath, mode='r')
        df = transformer1(input)

        transformer2 = self.get_transformer(pd.DataFrame, BIOMV210Format)
        obs = transformer2(df)
        self.assertIsInstance(obs, BIOMV210Format)

    def test_to_pandas_data_frame_to_biom_table(self):
        # load a table to a pd.DataFrame
        filepath = self.get_data_path('feature-table_v100.biom')
        transformer1 = self.get_transformer(BIOMV100Format, pd.DataFrame)
        input = BIOMV100Format(filepath, mode='r')
        df = transformer1(input)

        transformer2 = self.get_transformer(pd.DataFrame, biom.Table)
        obs = transformer2(df)
        self.assertIsInstance(obs, biom.Table)

    def test_biom_table_to_taxonomy_format(self):
        transformer = self.get_transformer(biom.Table, TaxonomyFormat)

        data = np.arange(16).reshape(4, 4)
        observation_ids = ['O%d' % i for i in range(4)]
        sample_ids = ['S%d' % i for i in range(4)]
        sample_metadata = [dict(x=i) for i in range(4)]
        observation_metadata = [dict(taxonomy=['a', 'b']) for _ in range(4)]

        table = biom.Table(data, observation_ids, sample_ids,
                           observation_metadata, sample_metadata)
        obs = transformer(table)

        self.assertIsInstance(obs, TaxonomyFormat)
        self.assertEqual(
            obs.path.read_text(),
            'Feature ID\tTaxon\nO0\ta; b\nO1\ta; b\nO2\ta; b\nO3\ta; b\n')

    def test_biom_table_to_taxonomy_format_no_taxonomy_md(self):
        transformer = self.get_transformer(biom.Table, TaxonomyFormat)

        data = np.arange(16).reshape(4, 4)
        observation_ids = ['O%d' % i for i in range(4)]
        sample_ids = ['S%d' % i for i in range(4)]
        sample_metadata = [dict(x=i) for i in range(4)]
        observation_metadata = [dict(taxon=['a', 'b']) for _ in range(4)]

        table = biom.Table(data, observation_ids, sample_ids,
                           observation_metadata, sample_metadata)

        with self.assertRaisesRegex(KeyError, 'does not contain `taxonomy`'):
            transformer(table)

    def test_biom_table_to_taxonomy_format_missing_md(self):
        transformer = self.get_transformer(biom.Table, TaxonomyFormat)

        data = np.arange(16).reshape(4, 4)
        observation_ids = ['O%d' % i for i in range(4)]
        sample_ids = ['S%d' % i for i in range(4)]
        sample_metadata = [dict(x=i) for i in range(4)]
        observation_metadata = [dict(taxonomy=['a', 'b']) for _ in range(4)]
        observation_metadata[2]['taxonomy'] = None

        table = biom.Table(data, observation_ids, sample_ids,
                           observation_metadata, sample_metadata)

        with self.assertRaisesRegex(TypeError, 'metadata must be specified'):
            transformer(table)

    def test_biom_v210_format_no_md_to_taxonomy_format(self):
        filepath = self.get_data_path('feature-table_v210.biom')
        transformer = self.get_transformer(BIOMV210Format, biom.Table)
        input = BIOMV210Format(filepath, mode='r')
        table = transformer(input)

        transformer = self.get_transformer(biom.Table, TaxonomyFormat)
        with self.assertRaisesRegex(TypeError, 'must have metadata'):
            transformer(table)


if __name__ == "__main__":
    unittest.main()
