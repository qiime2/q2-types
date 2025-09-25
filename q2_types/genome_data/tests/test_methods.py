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

import skbio
from qiime2.plugin.testing import TestPluginBase
from qiime2.plugins import types


from q2_types.feature_data import DNAFASTAFormat
from q2_types.genome_data import SeedOrthologDirFmt, collate_orthologs, \
    partition_orthologs, OrthologAnnotationDirFmt, \
    collate_ortholog_annotations, GenomeSequencesDirectoryFormat
from q2_types.genome_data import LociDirectoryFormat
from q2_types.genome_data._methods import collate_loci, collate_genomes


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

    def test_collate_genomes_dnafastaformat_single(self):
        self.helper_test_collate_genomes_dnafastaformat("single")

    def test_collate_genomes_dnafastaformat_multiple(self):
        self.helper_test_collate_genomes_dnafastaformat("multiple")

    def helper_test_collate_genomes_dnafastaformat(self, input):
        genomes1 = DNAFASTAFormat(
            self.get_data_path("dna-fasta-format/dna-sequences1.fasta"), "r"
        )
        genomes2 = DNAFASTAFormat(
            self.get_data_path("dna-fasta-format/dna-sequences2.fasta"), "r"
        )
        if input == "single":
            genomes = [genomes1]
            content = {
                "ref1": {"description": "d_Bacteria_1",
                         "sequence": "ACGTACGT"},
                "ref2": {"description": "d_Bacteria_2",
                         "sequence": "CGTCGTCC"},
            }
            exp_files = ["ref1.fasta", "ref2.fasta"]
        else:
            genomes = [genomes1, genomes2]
            content = {
                "ref1": {"description": "d_Bacteria_1",
                         "sequence": "ACGTACGT"},
                "ref2": {"description": "d_Bacteria_2",
                         "sequence": "CGTCGTCC"},
                "ref5": {"description": "d_Bacteria_3",
                         "sequence": "ACGTACGT"},
                "ref6": {"description": "d_Bacteria_4",
                         "sequence": "CGTCGTCC"},
            }
            exp_files = [
                "ref1.fasta", "ref2.fasta", "ref5.fasta", "ref6.fasta"
            ]

        collated_genomes = collate_genomes(genomes=genomes)
        actual_files = sorted(os.listdir(collated_genomes.path))
        self.assertEqual(actual_files, exp_files)

        for fn in actual_files:
            fp = os.path.join(collated_genomes.path, fn)
            with open(fp, "r") as fasta_file:
                for seq in skbio.io.read(fasta_file, "fasta"):
                    actual_id = seq.metadata["id"]
                    actual_description = seq.metadata["description"]
                    actual_sequence = str(seq)
                    expected_id = fn.split(".")[0]
                    expected_desc = content[expected_id]["description"]
                    expected_sequence = content[expected_id]["sequence"]

                    self.assertEquals(actual_id, expected_id)
                    self.assertEqual(actual_description, expected_desc)
                    self.assertEqual(actual_sequence, expected_sequence)

    def test_collate_genomes_genome_dir_multiple(self):
        genomes1 = GenomeSequencesDirectoryFormat(
            self.get_data_path("genomes-dir-format1"), "r"
        )
        genomes2 = GenomeSequencesDirectoryFormat(
            self.get_data_path("genomes-dir-format2"), "r"
        )
        genomes = [genomes1, genomes2]
        collated_genomes = collate_genomes(genomes=genomes)
        exp_files = ["ref1.fasta", "ref2.fasta", "ref3.fasta"]
        actual_files = sorted(os.listdir(collated_genomes.path))
        self.assertEqual(exp_files, actual_files)

    def test_collate_genomes_mix(self):
        # should throw TypeError
        genomes1 = DNAFASTAFormat(
            self.get_data_path("dna-fasta-format/dna-sequences1.fasta"), "r"
        )
        genomes2 = GenomeSequencesDirectoryFormat(
            self.get_data_path("genomes-dir-format2"), "r"
        )
        genomes = [genomes2, genomes1]
        with self.assertRaises(TypeError):
            types.methods.collate_genomes(genomes=genomes)

    def test_collate_genomes_duplicates_warn_genome(self):
        self.helper_test_collate_genomes_duplicates_warn("GenomeData")

    def test_collate_genomes_duplicates_warn_dna(self):
        self.helper_test_collate_genomes_duplicates_warn("DNAFASTAFormat")

    def helper_test_collate_genomes_duplicates_warn(self, dir_fmt):
        duplicate_ids = (
            ["ref1.fasta", "ref2.fasta"]
            if dir_fmt == "GenomeData"
            else ["ref1", "ref2"]
        )
        warn_msg = (
            "Duplicate sequence files were found for the following IDs: {}. "
            "The latest occurrence will overwrite all previous occurrences "
            "for each corresponding ID."
        ).format(", ".join(duplicate_ids))
        if dir_fmt == "GenomeData":
            genomes1 = GenomeSequencesDirectoryFormat(
                self.get_data_path("genomes-dir-format1"), "r"
            )
        else:
            genomes1 = DNAFASTAFormat(
                self.get_data_path("dna-fasta-format/dna-sequences1.fasta"),
                "r"
            )
        with warnings.catch_warnings(record=True) as w:
            collated_genomes = collate_genomes(genomes=[genomes1, genomes1])
            exp_files = ["ref1.fasta", "ref2.fasta"]
            actual_files = sorted(os.listdir(collated_genomes.path))
            self.assertEqual(actual_files, exp_files)
            self.assertEqual(warn_msg, str(w[0].message))

            if dir_fmt == "DNAFASTAFormat":
                content = {
                    "ref1": {"description": "d_Bacteria_1",
                             "sequence": "ACGTACGT"},
                    "ref2": {"description": "d_Bacteria_2",
                             "sequence": "CGTCGTCC"},
                }

                for fn in actual_files:
                    fp = os.path.join(collated_genomes.path, fn)
                    with open(fp, "r") as fasta_file:
                        for seq in skbio.io.read(fasta_file, "fasta"):
                            actual_id = seq.metadata["id"]
                            actual_description = seq.metadata["description"]
                            actual_sequence = str(seq)
                            expected_id = fn.split(".")[0]
                            expected_desc = content[expected_id]["description"]
                            exp_sequence = content[expected_id]["sequence"]

                            self.assertEquals(actual_id, expected_id)
                            self.assertEqual(actual_description, expected_desc)
                            self.assertEqual(actual_sequence, exp_sequence)

    def test_collate_genomes_duplicates_error_genome(self):
        self.helper_test_collate_genomes_duplicates_error("GenomeData")

    def test_collate_genomes_duplicates_error_dna(self):
        self.helper_test_collate_genomes_duplicates_error("DNAFASTAFormat")

    def helper_test_collate_genomes_duplicates_error(self, dir_fmt):
        duplicate_ids = ["ref3.fasta"] if dir_fmt == "GenomeData" else ["ref1"]
        error_msg = (
            "Duplicate sequence files were found for the "
            "following IDs: %s." % ", ".join(duplicate_ids)
        )
        if dir_fmt == "GenomeData":
            genomes1 = GenomeSequencesDirectoryFormat(
                self.get_data_path("genomes-dir-format2"), "r"
            )
        else:
            genomes1 = DNAFASTAFormat(
                self.get_data_path("dna-fasta-format/dna-sequences1.fasta"),
                "r"
            )
        with self.assertRaisesRegex(ValueError, error_msg):
            collate_genomes(
                genomes=[genomes1, genomes1], on_duplicates="error"
            )
