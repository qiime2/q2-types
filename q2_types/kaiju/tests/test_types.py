# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest

from qiime2.plugin.testing import TestPluginBase

from q2_types.kaiju import KaijuDB, KaijuDBDirectoryFormat


class TestTypes(TestPluginBase):
    package = "q2_types.kaiju.tests"

    def test_kaijudb_semantic_type_registration(self):
        self.assertRegisteredSemanticType(KaijuDB)

    def test_kaijudb_semantic_type_to_format_registration(self):
        self.assertSemanticTypeRegisteredToFormat(
            KaijuDB, KaijuDBDirectoryFormat
        )


if __name__ == "__main__":
    unittest.main()
