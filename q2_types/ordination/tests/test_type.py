# ----------------------------------------------------------------------------
# Copyright (c) 2016-2021, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest

from q2_types.ordination import (
    PCoAResults, OrdinationDirectoryFormat,
    ProcrustesM2Statistic, ProcrustesM2StatDFmt,
)


from qiime2.plugin.testing import TestPluginBase


class TestTypes(TestPluginBase):
    package = 'q2_types.ordination.tests'

    def test_pcoa_results_semantic_type_registration(self):
        self.assertRegisteredSemanticType(PCoAResults)

    def test_pcoa_results_semantic_type_to_ordination_fmt_registration(self):
        self.assertSemanticTypeRegisteredToFormat(PCoAResults,
                                                  OrdinationDirectoryFormat)

    def test_procrustes_m2_semantic_type_registration(self):
        self.assertRegisteredSemanticType(ProcrustesM2Statistic)

    def test_procrustes_m2_semantic_type_to_m2_fmt_registration(self):
        self.assertSemanticTypeRegisteredToFormat(ProcrustesM2Statistic,
                                                  ProcrustesM2StatDFmt)


if __name__ == "__main__":
    unittest.main()
