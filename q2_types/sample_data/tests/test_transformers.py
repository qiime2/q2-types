# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest

import pandas as pd
from pandas.testing import assert_series_equal

import qiime2
from qiime2.plugin.testing import TestPluginBase

from q2_types.sample_data import AlphaDiversityFormat


class TestTransformers(TestPluginBase):
    package = "q2_types.sample_data.tests"

    def test_pd_series_to_alpha_diversity_format(self):
        transformer = self.get_transformer(pd.Series, AlphaDiversityFormat)
        exp_index = pd.Index(['Sample1', 'Sample4'], dtype=object)
        exp = pd.Series([0.970950594455, 0.721928094887],
                        name='shannon', index=exp_index)

        obs = transformer(exp)

        obs = pd.read_csv(str(obs), sep='\t', header=0, index_col=0)
        # Squeeze into series instead of dataframe
        obs = obs.squeeze('columns')

        assert_series_equal(exp, obs)

    def test_alpha_diversity_format_to_pd_series(self):
        filename = 'alpha-diversity.tsv'
        _, obs = self.transform_format(AlphaDiversityFormat, pd.Series,
                                       filename)
        exp_index = pd.Index(['Sample1', 'Sample4'], dtype=object)
        exp = pd.Series([0.970950594455, 0.721928094887],
                        name='shannon', index=exp_index)
        assert_series_equal(exp, obs)

    def test_alpha_diversity_format_with_metadata_to_pd_series(self):
        filename = 'alpha-diversity-with-metadata.tsv'
        _, obs = self.transform_format(AlphaDiversityFormat, pd.Series,
                                       filename)
        exp_index = pd.Index(['Sample1', 'Sample4'], dtype=object)
        exp = pd.Series([0.970950594455, 0.721928094887],
                        name='shannon', index=exp_index)
        assert_series_equal(exp, obs)

    def test_alpha_diversity_format_to_pd_series_int_indices(self):
        filename = 'alpha-diversity-int-indices.tsv'
        _, obs = self.transform_format(AlphaDiversityFormat, pd.Series,
                                       filename)

        exp_index = pd.Index(['1', '4'], dtype=object)
        exp = pd.Series([0.97, 0.72], name='foo', index=exp_index)
        assert_series_equal(exp, obs)

    def test_alpha_diversity_format_to_metadata(self):
        filename = 'alpha-diversity.tsv'
        _, obs = self.transform_format(AlphaDiversityFormat, qiime2.Metadata,
                                       filename)

        exp_index = pd.Index(['Sample1', 'Sample4'], name='Sample ID',
                             dtype=object)
        exp_df = pd.DataFrame([[0.9709505944546688], [0.7219280948873623]],
                              columns=['shannon'], index=exp_index)
        exp_md = qiime2.Metadata(exp_df)

        self.assertEqual(obs, exp_md)

    def test_non_alpha_diversity(self):
        filename = 'also-not-alpha-diversity.tsv'
        with self.assertRaisesRegex(ValueError, 'Non-numeric values '):
            self.transform_format(AlphaDiversityFormat, pd.Series, filename)


if __name__ == '__main__':
    unittest.main()
