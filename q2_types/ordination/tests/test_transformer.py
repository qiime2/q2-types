# ----------------------------------------------------------------------------
# Copyright (c) 2016-2017, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest

import skbio

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


if __name__ == "__main__":
    unittest.main()
