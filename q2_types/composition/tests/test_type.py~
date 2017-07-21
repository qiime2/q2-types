# ----------------------------------------------------------------------------
# Copyright (c) 2016-2017, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest

from q2_gneiss.composition._type import Composition, Balance
from qiime2.plugin.testing import TestPluginBase


class TestTypes(TestPluginBase):
    package = "q2_gneiss.composition.tests"

    def test_composition_semantic_type_registration(self):
        self.assertRegisteredSemanticType(Composition)

    def test_balance_semantic_type_registration(self):
        self.assertRegisteredSemanticType(Balance)


if __name__ == '__main__':
    unittest.main()
