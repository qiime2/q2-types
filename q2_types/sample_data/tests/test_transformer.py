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
        input = pd.Series.from_csv(filename, sep='\t', header=0)

        obs = transformer(input)
        obs = pd.Series.from_csv(str(obs), sep='\t', header=0)

        assert_series_equal(input, obs)

    def test_alpha_diversity_format_to_pd_series(self):
        filename = 'alpha-diversity.tsv'
        input, obs = self.transform_format(AlphaDiversityFormat, pd.Series,
                                           filename)
        input = pd.Series.from_csv(str(input), sep='\t', header=0)

        assert_series_equal(input, obs)


if __name__ == '__main__':
    unittest.main()
