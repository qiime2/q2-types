# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import json
import unittest

from qiime2.plugin.testing import TestPluginBase

from q2_types.feature_map import MAGtoContigsFormat


class TestTransformers(TestPluginBase):
    package = "q2_types.feature_map.tests"

    def setUp(self):
        super().setUp()
        self.valid_contig_map = {
            "23c5b64e-3f3e-4688-9862-e9dae4fa0f5b": ["contig1", "contig2"],
            "70c5a728-96a6-4eed-b9f9-9a73153c1385": ["contig3"],
            "7e2a749a-a19a-4b62-8195-0ee601b5fdfb": [
                "contig1", "contig3", "contig4"
            ],
            "6232c7e1-8ed7-47c8-9bdb-b94706a26931": ["contig2", "contig5"],
        }

    def test_contig_map_to_dict(self):
        transformer = self.get_transformer(MAGtoContigsFormat, dict)
        _input = MAGtoContigsFormat(
            self.get_data_path("mag-to-contigs-valid.json"), "r"
        )

        obs = transformer(_input)
        self.assertDictEqual(self.valid_contig_map, obs)

    def test_dict_to_contig_map(self):
        transformer = self.get_transformer(dict, MAGtoContigsFormat)
        obs_fp = transformer(self.valid_contig_map)

        with obs_fp.open() as obs_fh:
            obs = json.load(obs_fh)
        self.assertDictEqual(self.valid_contig_map, obs)


if __name__ == "__main__":
    unittest.main()
