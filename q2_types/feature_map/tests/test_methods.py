# ----------------------------------------------------------------------------
# Copyright (c) 2026, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
from qiime2.plugin.testing import TestPluginBase

from q2_types.feature_map import collate_contig_maps


class TestCollateContigMaps(TestPluginBase):
    package = "q2_types.feature_map.tests"

    def test_collate_contig_maps(self):
        contig_maps = [
            {"mag1": ["contig1", "contig2"]},
            {"mag2": ["contig3"], "mag3": ["contig4", "contig5"]},
        ]

        obs = collate_contig_maps(contig_maps)

        exp = {
            "mag1": ["contig1", "contig2"],
            "mag2": ["contig3"],
            "mag3": ["contig4", "contig5"],
        }
        self.assertDictEqual(exp, obs)
