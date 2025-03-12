# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import filecmp
from unittest.mock import patch

from qiime2.plugin.testing import TestPluginBase

from q2_types.per_sample_sequences import MultiMAGSequencesDirFmt
from q2_types.per_sample_sequences._methods import (
    partition_sample_data_mags, collate_sample_data_mags
)


class TestSampleDataMAGsPartitionCollating(TestPluginBase):
    package = "q2_types.per_sample_sequences.tests"

    @patch("q2_types._util._validate_mag_ids")
    @patch("q2_types._util._validate_num_partitions")
    def test_partition_sample_data_mags(
        self,
        mock_validate_num_partitions,
        mock_validate_mag_ids
    ):
        # Partition mags
        p = self.get_data_path("collated_mags")
        mags = MultiMAGSequencesDirFmt(path=p, mode="r")
        mock_validate_num_partitions.return_value = 2
        partitioned_mags = partition_sample_data_mags(mags, 2)

        # Expected mag ids for every sample
        mag_ids_sample_1 = [
            "24dee6fe-9b84-45bb-8145-de7b092533a1.fasta",
            "fb0bc871-04f6-486b-a10e-8e0cb66f8de3.fasta"
        ]
        mag_ids_sample_2 = [
            "d65a71fa-4279-4588-b937-0747ed5d604d.fasta",
        ]

        # Compare dirs
        exp_partitions = [
            ("sample1", mag_ids_sample_1), ("sample2", mag_ids_sample_2)
        ]
        for _id, mag_ids in exp_partitions:
            dircmp = filecmp.dircmp(
                partitioned_mags[_id].path,
                mags.path
            )
            self.assertListEqual(
                ["MANIFEST", _id], dircmp.common
            )
            dircmp = filecmp.dircmp(
                f"{partitioned_mags[_id].path}/{_id}",
                f"{mags.path}/{_id}"
            )
            self.assertListEqual(
                [
                    *mag_ids,
                ],
                dircmp.common
            )

    def test_collate_sample_data_mags(self):
        p1 = self.get_data_path("partitioned_mags/mag1")
        p2 = self.get_data_path("partitioned_mags/mag2")
        mags = [
            MultiMAGSequencesDirFmt(p1, mode="r"),
            MultiMAGSequencesDirFmt(p2, mode="r")
        ]

        collated_mags = collate_sample_data_mags(mags)
        expected = self.get_data_path("collated_mags")

        # compare first dir
        dircmp = filecmp.dircmp(collated_mags.path, expected)
        self.assertListEqual(["MANIFEST", "sample1", "sample2"], dircmp.common)

        # Compare second dir
        dircmp = filecmp.dircmp(
            f"{collated_mags.path}/sample1",
            f"{expected}/sample1"
        )
        self.assertListEqual(
            [
                "24dee6fe-9b84-45bb-8145-de7b092533a1.fasta",
                "fb0bc871-04f6-486b-a10e-8e0cb66f8de3.fasta"
            ],
            dircmp.common
        )

        # compare third dir
        dircmp = filecmp.dircmp(
            f"{collated_mags.path}/sample2",
            f"{expected}/sample2"
        )
        self.assertListEqual(
            ["d65a71fa-4279-4588-b937-0747ed5d604d.fasta"],
            dircmp.common
        )

        # compare MANIFEST
        self.assertTrue(
            filecmp.cmp(
                f"{collated_mags.path}/MANIFEST",
                f"{expected}/MANIFEST"
            )
        )
