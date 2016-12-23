# ----------------------------------------------------------------------------
# Copyright (c) 2016-2017, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import os
import shutil
import unittest

from q2_types.feature_data import (
    TaxonomyFormat, TaxonomyDirectoryFormat, DNAFASTAFormat,
    DNASequencesDirectoryFormat, PairedDNASequencesDirectoryFormat,
    AlignedDNAFASTAFormat, AlignedDNASequencesDirectoryFormat
)
from qiime2.plugin.testing import TestPluginBase


class TestFormats(TestPluginBase):
    package = 'q2_types.feature_data.tests'

    # Taxonomy Format and Directory Tests
    def test_taxonomy_format_validate_positive(self):
        filepath = self.get_data_path('taxonomy.tsv')
        format = TaxonomyFormat(filepath, mode='r')

        format.validate()

    def test_taxonomy_format_validate_negative(self):
        filepath = self.get_data_path('not-taxonomy')
        format = TaxonomyFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValueError, 'Taxonomy'):
            format.validate()

    def test_taxonomy_directory_format(self):
        filepath = self.get_data_path('taxonomy.tsv')
        shutil.copy(filepath,
                    os.path.join(self.temp_dir.name, 'taxonomy.tsv'))
        format = TaxonomyDirectoryFormat(self.temp_dir.name, mode='r')

        format.validate()

    # FASTA DNA Format and Directory Tests
    def test_dna_fasta_format_validate_positive(self):
        filepath = self.get_data_path('dna-sequences.fasta')
        format = DNAFASTAFormat(filepath, mode='r')

        format.validate()

    def test_dna_fasta_format_validate_negative(self):
        filepath = self.get_data_path('not-dna-sequences')
        format = DNAFASTAFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValueError, 'DNAFASTA'):
            format.validate()

    def test_dna_sequences_directory_format(self):
        filepath = self.get_data_path('dna-sequences.fasta')
        shutil.copy(filepath,
                    os.path.join(self.temp_dir.name, 'dna-sequences.fasta'))
        format = DNASequencesDirectoryFormat(self.temp_dir.name, mode='r')

        format.validate()

    def test_paired_dna_sequences_directory_format(self):
        filepath = self.get_data_path('dna-sequences.fasta')
        temp_dir = self.temp_dir.name
        left_seq = os.path.join(temp_dir, 'left-dna-sequences.fasta')
        right_seq = os.path.join(temp_dir, 'right-dna-sequences.fasta')

        shutil.copy(filepath, left_seq)
        shutil.copy(filepath, right_seq)

        format = PairedDNASequencesDirectoryFormat(temp_dir, mode='r')

        format.validate()

    def test_aligned_dna_fasta_format_validate_positive(self):
        filepath = self.get_data_path('aligned-dna-sequences.fasta')
        format = AlignedDNAFASTAFormat(filepath, mode='r')

        format.validate()

    def test_aligned_dna_fasta_format_validate_negative(self):
        filepath = self.get_data_path('not-dna-sequences')
        format = AlignedDNAFASTAFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValueError, 'AlignedDNAFASTA'):
            format.validate()

    def test_aligned_dna_sequences_directory_format(self):
        filepath = self.get_data_path('aligned-dna-sequences.fasta')
        temp_dir = self.temp_dir.name
        shutil.copy(filepath,
                    os.path.join(temp_dir, 'aligned-dna-sequences.fasta'))
        format = AlignedDNASequencesDirectoryFormat(temp_dir, mode='r')

        format.validate()


if __name__ == '__main__':
    unittest.main()
