# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
from qiime2.plugin.testing import TestPluginBase
from . import HMM


class TestHMMType(TestPluginBase):
    package = 'q2_types.reference_db.tests'

    def test_hmmer_registration(self):
        self.assertRegisteredSemanticType(...)

    def test_HMMER_semantic_type_registered_to_DirFmt(self):
        self.assertSemanticTypeRegisteredToFormat(
            HMM[...], ...
        )
