# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import filecmp
import os
import warnings

from qiime2.plugin.testing import TestPluginBase

from q2_types.genome_data import SeedOrthologDirFmt, collate_orthologs, \
    partition_orthologs, OrthologAnnotationDirFmt, collate_ortholog_annotations
from q2_types.genome_data import LociDirectoryFormat
from q2_types.genome_data._methods import collate_loci


class TestOrthologsPartitionCollating(TestPluginBase):
    package = "q2_types.genome_data.tests"

    def test_collate_orthologs(self):
        p1 = self.get_data_path("partitioned_orthologs/ortholog_1")
        p2 = self.get_data_path("partitioned_orthologs/ortholog_2")
        orthologs = [
            SeedOrthologDirFmt(p1, mode="r"),
            SeedOrthologDirFmt(p2, mode="r")
        ]

        collated_orthologs = collate_orthologs(orthologs)
        self.assertTrue(os.path.exists(
            collated_orthologs.path / "1.emapper.seed_orthologs")
        )
        self.assertTrue(os.path.exists(
            collated_orthologs.path / "2.emapper.seed_orthologs")
        )

    def test_collate_loci(self):
        p1 = self.get_data_path("uncollated_loci_1")
        p2 = self.get_data_path("uncollated_loci_2")
        loci_list = [
            LociDirectoryFormat(p1, mode="r"),
            LociDirectoryFormat(p2, mode="r")
        ]

        collated_loci = collate_loci(loci_list)
        self.assertTrue(all(os.path.exists(
            collated_loci.path / f"loci{no}.gff") for no in [1, 2, 3, 4]))

    def test_collate_loci_file_exists(self):
        p1 = self.get_data_path("uncollated_loci_1")
        loci_list = [
            LociDirectoryFormat(p1, mode="r"),
            LociDirectoryFormat(p1, mode="r")
        ]

        with warnings.catch_warnings(record=True) as w:
            collated_loci = collate_loci(loci_list)
            self.assertIn("File already exists", str(w[-1].message))

            self.assertTrue(all(os.path.exists(
                    collated_loci.path / f"loci{no}.gff") for no in [1, 2]))

    def test_partition_orthologs(self):
        p = self.get_data_path("collated_orthologs")
        orthologs = SeedOrthologDirFmt(path=p, mode="r")
        obs = partition_orthologs(orthologs, 2)

        self.assertTrue(os.path.exists(
            obs["1"].path / "1.emapper.seed_orthologs")
        )
        self.assertTrue(os.path.exists(
            obs["1"].path / "1.emapper.seed_orthologs")
        )

    def test_partition_orthologs_warning_message(self):
        path = self.get_data_path("collated_orthologs")
        orthologs = SeedOrthologDirFmt(path=path, mode="r")

        with self.assertWarnsRegex(
            UserWarning, "You have requested a number of.*5.*2.*2"
        ):
            partition_orthologs(orthologs, 5)

    def test_collate_ortholog_annotations(self):
        p = self.get_data_path("ortholog-annotations-collating")
        annotations = [
          OrthologAnnotationDirFmt(f"{p}/{letter}", mode="r")
          for letter in ["a", "b", "c"]
        ]
        collated_annotations = collate_ortholog_annotations(annotations)

        # assert that all files are there
        compare = filecmp.dircmp(
            collated_annotations.path,
            self.get_data_path("ortholog-annotations-collating/collated")
        )
        self.assertListEqual(
            compare.common,
            [f"{letter}.annotations" for letter in ["a", "b", "c"]]
        )
