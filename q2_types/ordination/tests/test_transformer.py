# ----------------------------------------------------------------------------
# Copyright (c) 2016-2017, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest

import skbio
import pandas as pd
from pandas.util.testing import assert_frame_equal, assert_series_equal

import qiime2
from q2_types.ordination import OrdinationFormat
from qiime2.plugin.testing import TestPluginBase


class TestTransformers(TestPluginBase):
    package = 'q2_types.ordination.tests'

    def test_skbio_ordination_results_to_ordination_format(self):
        filenames = ('pcoa-results-1x1.txt', 'pcoa-results-2x2.txt',
                     'pcoa-results-NxN.txt')
        for filename in filenames:
            filepath = self.get_data_path(filename)
            transformer = self.get_transformer(skbio.OrdinationResults,
                                               OrdinationFormat)
            input = skbio.OrdinationResults.read(filepath)

            obs = transformer(input)
            self.assertIsInstance(obs, OrdinationFormat)
            obs = skbio.OrdinationResults.read(str(obs))

            self.assertEqual(str(obs), str(input))

    def test_ordination_format_to_skbio_ordination_results(self):
        filenames = ('pcoa-results-1x1.txt', 'pcoa-results-2x2.txt',
                     'pcoa-results-NxN.txt')
        for filename in filenames:
            input, obs = self.transform_format(OrdinationFormat,
                                               skbio.OrdinationResults,
                                               filename=filename)
            exp = skbio.OrdinationResults.read(str(input))

            self.assertEqual(str(exp), str(obs))

    def test_ordination_format_to_dataframe_1x1(self):
        _, obs = self.transform_format(OrdinationFormat, pd.DataFrame,
                                       'pcoa-results-1x1.txt')

        index = pd.Index(['s1'], name='ID', dtype=object)
        exp = pd.DataFrame([0.0], index=index, columns=['Column 1'],
                           dtype=float)

        assert_frame_equal(exp, obs)

    def test_ordination_format_to_dataframe_2x2(self):
        _, obs = self.transform_format(OrdinationFormat, pd.DataFrame,
                                       'pcoa-results-2x2.txt')

        index = pd.Index(['s1', 's2'], name='ID', dtype=object)
        exp = pd.DataFrame([[-21.0, 0.0], [21, 0.0]], index=index,
                           columns=['Column 1', 'Column 2'], dtype=float)

        assert_frame_equal(exp, obs)

    def test_ordination_format_to_dataframe_NxN(self):
        _, obs = self.transform_format(OrdinationFormat, pd.DataFrame,
                                       'pcoa-results-NxN.txt')

        columns = ['Column %d' % i for i in range(1, 9)]
        self.assertEqual(columns, sorted(list(obs.columns.values)))

        ids = ['f1', 'f2', 'f3', 'f4', 'p1', 'p2', 't1', 't2']
        self.assertEqual(ids, sorted(obs.index.values))

    def test_ordination_format_to_metadata(self):
        _, obs = self.transform_format(OrdinationFormat, qiime2.Metadata,
                                       'pcoa-results-2x2.txt')

        categories = ['Column 1', 'Column 2']
        index = pd.Index(['s1', 's2'], name='ID', dtype=object)
        exp = pd.DataFrame([[-21.0, 0.0], [21, 0.0]], columns=categories,
                           index=index, dtype=float)

        self.assertEqual({'s1', 's2'}, obs.ids())

        for category in categories:
            assert_series_equal(obs.get_category(category).to_series(),
                                exp[category])


if __name__ == "__main__":
    unittest.main()
