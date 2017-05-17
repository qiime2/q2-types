# ----------------------------------------------------------------------------
# Copyright (c) 2016-2017, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest

import pandas as pd

from pandas.util.testing import assert_series_equal
from q2_types.sample_data import AlphaDiversityFormat
from qiime2.plugin.testing import TestPluginBase


class TestTransformers(TestPluginBase):
    package = "q2_types.sample_data.tests"

    def test_pd_series_to_alpha_diversity_format(self):
        filename = self.get_data_path('alpha-diversity.tsv')
        transformer = self.get_transformer(pd.Series, AlphaDiversityFormat)
        exp_index = pd.Index(['Sample1', 'Sample4'], dtype=object)
        exp = pd.Series([0.970950594455, 0.721928094887],
                        name='shannon', index=exp_index)

        obs = transformer(exp)
        obs = pd.Series.from_csv(str(obs), sep='\t', header=0)

        assert_series_equal(exp, obs)

    def test_alpha_diversity_format_to_pd_series(self):
        filename = 'alpha-diversity.tsv'
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

    def test_non_alpha_diversity(self):
        filename = 'also-not-alpha-diversity.tsv'
        with self.assertRaisesRegex(ValueError, 'Unable to parse string'):
            self.transform_format(AlphaDiversityFormat, pd.Series, filename)


if __name__ == '__main__':
    unittest.main()
