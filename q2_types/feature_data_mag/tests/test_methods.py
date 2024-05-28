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

from q2_types.feature_data_mag import MAGSequencesDirFmt, \
    OrthologAnnotationDirFmt
from q2_types.feature_data_mag._methods import partition_feature_data_mags, \
    collate_feature_data_mags, collate_ortholog_annotations


class TestFeatureDataMAGsPartitionCollating(TestPluginBase):
    package = "q2_types.feature_data_mag.tests"

    @patch("q2_types._util._validate_mag_ids")
    @patch("q2_types._util._validate_num_partitions")
    def test_partition_feature_data_mags(
        self,
        mock_validate_num_partitions,
        mock_validate_mag_ids
    ):
        # Partition Feature Data
        p = self.get_data_path("collated_mags")
        mags = MAGSequencesDirFmt(path=p, mode="r")
        mock_validate_num_partitions.return_value = 2
        partitioned_mags = partition_feature_data_mags(mags)

        # Expected mag ids
        mag_ids = [
            "24dee6fe-9b84-45bb-8145-de7b092533a1",
            "fb0bc871-04f6-486b-a10e-8e0cb66f8de3"
        ]

        # compare partitions
        for i in [0, 1]:
            dircmp = filecmp.dircmp(
                partitioned_mags[mag_ids[i]].path, mags.path
            )
            self.assertListEqual([f"{mag_ids[i]}.fasta"], dircmp.common)

    def test_collate_feature_data_mags(self):
        # collate test data
        p1 = self.get_data_path("partitioned_mags/mag1")
        p2 = self.get_data_path("partitioned_mags/mag2")
        mags = [
            MAGSequencesDirFmt(p1, mode="r"),
            MAGSequencesDirFmt(p2, mode="r")
        ]
        collated_mags = collate_feature_data_mags(mags)

        # compare directories
        expected = self.get_data_path("collated_mags")
        dircmp = filecmp.dircmp(collated_mags.path, expected)
        self.assertListEqual(
            [
                "24dee6fe-9b84-45bb-8145-de7b092533a1.fasta",
                "fb0bc871-04f6-486b-a10e-8e0cb66f8de3.fasta"
            ],
            dircmp.common
        )

    def test_collate_ortholog_annotations(self):
        p = self.get_data_path("partitioned_ortholog_annotations")
        annotations = [
          OrthologAnnotationDirFmt(f"{p}/{letter}", mode="r")
          for letter in ["a", "b", "c"]
        ]
        collated_annotations = collate_ortholog_annotations(annotations)

        # assert that all files are there
        compare = filecmp.dircmp(
            collated_annotations.path,
            self.get_data_path("collated_ortholog_annotations")
        )
        self.assertListEqual(
            compare.common,
            [f"{letter}.annotations" for letter in ["a", "b", "c"]]
        )