# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest

from qiime2.plugin.testing import TestPluginBase


from q2_types.genome_data import (
    GenomeData, Genes, Proteins, Loci, GenesDirectoryFormat,
    ProteinsDirectoryFormat, LociDirectoryFormat, SeedOrthologDirFmt,
    Orthologs, GenomeSequencesDirectoryFormat, DNASequence, NOG,
    OrthologAnnotationDirFmt
)
from q2_types.sample_data import SampleData


class TestTypes(TestPluginBase):
    package = 'q2_types.genome_data.tests'

    def test_genome_data_semantic_type_registration(self):
        self.assertRegisteredSemanticType(GenomeData)

    def test_genes_semantic_type_registration(self):
        self.assertRegisteredSemanticType(Genes)

    def test_proteins_semantic_type_registration(self):
        self.assertRegisteredSemanticType(Proteins)

    def test_loci_semantic_type_registration(self):
        self.assertRegisteredSemanticType(Loci)

    def test_sequence_semantic_type_registration(self):
        self.assertRegisteredSemanticType(DNASequence)

    def test_orthologs_semantic_type_registration(self):
        self.assertRegisteredSemanticType(Orthologs)

    def test_nog_semantic_type_registration(self):
        self.assertRegisteredSemanticType(NOG)

    def test_genome_data_genes_to_genes_dir_fmt_registration(self):
        self.assertSemanticTypeRegisteredToFormat(
            GenomeData[Genes], GenesDirectoryFormat)

    def test_genome_data_proteins_to_proteins_dir_fmt_registration(self):
        self.assertSemanticTypeRegisteredToFormat(
            GenomeData[Proteins], ProteinsDirectoryFormat)

    def test_genome_data_loci_to_loci_dir_fmt_registration(self):
        self.assertSemanticTypeRegisteredToFormat(
            GenomeData[Loci], LociDirectoryFormat)

    def test_genome_data_nog_registered_to_seedorthologdirfmt(self):
        self.assertSemanticTypeRegisteredToFormat(
            GenomeData[NOG], OrthologAnnotationDirFmt)

    def test_genome_data_orthologs_registered_to_seedorthologdirfmt(self):
        self.assertSemanticTypeRegisteredToFormat(
            GenomeData[Orthologs], SeedOrthologDirFmt)

    def test_genome_data_sequence_to_genome_dir_fmt_registration(self):
        self.assertSemanticTypeRegisteredToFormat(
            GenomeData[DNASequence], GenomeSequencesDirectoryFormat)

    def test_sample_data_orthologs_registered_to_seedorthologdirfmt(self):
        self.assertSemanticTypeRegisteredToFormat(
            SampleData[Orthologs], SeedOrthologDirFmt)

    def test_sample_data_nog_registered_to_seedorthologdirfmt(self):
        self.assertSemanticTypeRegisteredToFormat(
            SampleData[NOG], OrthologAnnotationDirFmt)


if __name__ == '__main__':
    unittest.main()
