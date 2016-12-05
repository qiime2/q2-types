# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest

import skbio

from q2_types.ordination import OrdinationFormat
from qiime.plugin.testing import TestPluginBase


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

    def test_ordination_format_to_skbio_ordination_results(self):
        filenames = ('pcoa-results-1x1.txt', 'pcoa-results-2x2.txt',
                     'pcoa-results-NxN.txt')
        for filename in filenames:
            filepath = self.get_data_path(filename)
            transformer = self.get_transformer(OrdinationFormat,
                                               skbio.OrdinationResults)
            input = OrdinationFormat(filepath, mode='r')

            obs = transformer(input)

            self.assertIsInstance(obs, skbio.OrdinationResults)


if __name__ == "__main__":
    unittest.main()
