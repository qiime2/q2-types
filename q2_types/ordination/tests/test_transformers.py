# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest

import skbio
import pandas as pd
import pandas.testing as pdt

import qiime2
from qiime2.plugin.testing import TestPluginBase

from q2_types.ordination import OrdinationFormat, ProcrustesStatisticsFmt


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

    def test_1x1_ordination_format_to_metadata(self):
        _, obs = self.transform_format(OrdinationFormat, qiime2.Metadata,
                                       'pcoa-results-1x1.txt')

        index = pd.Index(['s1'], name='Sample ID', dtype=object)
        exp_df = pd.DataFrame([0.0], index=index, columns=['Axis 1'],
                              dtype=float)
        exp = qiime2.Metadata(exp_df)

        self.assertEqual(exp, obs)

    def test_2x2_ordination_format_to_metadata(self):
        _, obs = self.transform_format(OrdinationFormat, qiime2.Metadata,
                                       'pcoa-results-2x2.txt')

        index = pd.Index(['s1', 's2'], name='Sample ID', dtype=object)
        exp_df = pd.DataFrame([[-20.999999999999996, -0.0],
                               [20.999999999999996, -0.0]], index=index,
                              columns=['Axis 1', 'Axis 2'], dtype=float)
        exp = qiime2.Metadata(exp_df)

        self.assertEqual(exp, obs)

    def test_NxN_ordination_format_to_metadata(self):
        # Not creating a reference dataframe here because manually populating
        # that DataFrame is a pain. Specifically we just want to check the
        # functionality of the dynamic column naming (e.g. Axis N).
        _, obs = self.transform_format(OrdinationFormat, qiime2.Metadata,
                                       'pcoa-results-NxN.txt')

        columns = ['Axis %d' % i for i in range(1, 9)]
        self.assertEqual(columns, list(obs.columns))

    def test_df_to_procrustes_m2_stats_fmt(self):
        input_df = pd.DataFrame({'true M^2 value': [1],
                                 'p-value for true M^2 value': [0.2],
                                 'number of Monte Carlo permutations': [300]},
                                index=pd.Index(['results'], name='id'))

        exp = ['id\ttrue M^2 value\tp-value for true M^2 value\t'
               'number of Monte Carlo permutations\n',
               '#q2:types\tnumeric\tnumeric\tnumeric\n',
               'results\t1\t0.2\t300\n']

        transformer = self.get_transformer(pd.DataFrame,
                                           ProcrustesStatisticsFmt)
        fmt = transformer(input_df)
        with open(str(fmt), 'r') as fh:
            obs = fh.readlines()

        self.assertEqual(exp, obs)

    def test_procrustes_m2_stats_fmt_to_df(self):
        filepath = self.get_data_path('m2stats-999-permus.tsv')
        input_fmt = ProcrustesStatisticsFmt(filepath, mode='r')
        exp = pd.DataFrame({'true M^2 value': [0.0789623748362618],
                            'p-value for true M^2 value': [0.001],
                            'number of Monte Carlo permutations': [999]},
                           index=pd.Index(['results'], name='id'))

        transformer = self.get_transformer(ProcrustesStatisticsFmt,
                                           pd.DataFrame)
        obs = transformer(input_fmt)

        pdt.assert_frame_equal(exp, obs)

    def test_procrustes_m2_stats_fmt_to_md(self):
        filepath = self.get_data_path('m2stats-999-permus.tsv')
        input_fmt = ProcrustesStatisticsFmt(filepath, mode='r')
        df = pd.DataFrame({'true M^2 value': [0.0789623748362618],
                           'p-value for true M^2 value': [0.001],
                           'number of Monte Carlo permutations': [999]},
                          index=pd.Index(['results'], name='id'))
        exp = qiime2.Metadata(df)

        transformer = self.get_transformer(ProcrustesStatisticsFmt,
                                           qiime2.Metadata)
        obs = transformer(input_fmt)

        self.assertEqual(exp, obs)


if __name__ == "__main__":
    unittest.main()
