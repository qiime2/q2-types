# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------


import skbio

from q2_types.ordination import OrdinationFormat
from qiime.plugin.testing import TestPluginBase


class TestTransformers(TestPluginBase):
    package = 'q2_types.ordination.tests'

    def test_skbio_ordination_results_to_ordination_format(self):
        filepath = self.get_data_path('pcoa-results.txt')
        transformer = self.get_transformer(skbio.OrdinationResults,
                                           OrdinationFormat)
        input = skbio.OrdinationResults.read(filepath)

        obs = transformer(input)

        self.assertIsInstance(obs, OrdinationFormat)

    def test_ordination_format_to_skbio_ordination_results(self):
        filepath = self.get_data_path('pcoa-results.txt')
        transformer = self.get_transformer(OrdinationFormat,
                                           skbio.OrdinationResults)
        input = OrdinationFormat(filepath, mode='r')

        obs = transformer(input)

        self.assertIsInstance(obs, skbio.OrdinationResults)
