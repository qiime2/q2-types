# ----------------------------------------------------------------------------
# Copyright (c) 2016-2019, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import os
import os.path
import shutil
import unittest

from q2_types.feature_data import (
    TaxonomyFormat, TaxonomyDirectoryFormat, HeaderlessTSVTaxonomyFormat,
    HeaderlessTSVTaxonomyDirectoryFormat, TSVTaxonomyFormat,
    TSVTaxonomyDirectoryFormat, DNAFASTAFormat, DNASequencesDirectoryFormat,
    PairedDNASequencesDirectoryFormat, AlignedDNAFASTAFormat,
    AlignedDNASequencesDirectoryFormat
)
from qiime2.plugin.testing import TestPluginBase
from qiime2.plugin import ValidationError


class TestTaxonomyFormats(TestPluginBase):
    package = 'q2_types.feature_data.tests'

    def test_taxonomy_format_validate_positive(self):
        filenames = ['headerless.tsv', '2-column.tsv', '3-column.tsv',
                     'valid-but-messy.tsv', 'many-rows.tsv']
        filepaths = [self.get_data_path(os.path.join('taxonomy', filename))
                     for filename in filenames]

        for filepath in filepaths:
            format = TaxonomyFormat(filepath, mode='r')

            format.validate()

    def test_taxonomy_format_validate_negative(self):
        filenames = ['empty', 'blanks-and-comments', '1-column.tsv']
        filepaths = [self.get_data_path(os.path.join('taxonomy', filename))
                     for filename in filenames]

        for filepath in filepaths:
            format = TaxonomyFormat(filepath, mode='r')

            with self.assertRaisesRegex(ValidationError, 'Taxonomy'):
                format.validate()

    def test_taxonomy_directory_format(self):
        # Basic test to verify that single-file directory format is working.
        filepath = self.get_data_path(os.path.join('taxonomy', '2-column.tsv'))
        shutil.copy(filepath,
                    os.path.join(self.temp_dir.name, 'taxonomy.tsv'))

        format = TaxonomyDirectoryFormat(self.temp_dir.name, mode='r')

        format.validate()

    # NOTE: the tests below for HeaderlessTSVTaxonomyFormat use some test files
    # that have headers. However, it makes no difference to this file format
    # since the header will be interpreted as data and exercises the correct
    # codepaths in the sniffer.
    #
    # These tests are nearly identical to the tests above for TaxonomyFormat --
    # the sniffer operates in exactly the same way (the transformers, however,
    # differ in behavior).

    def test_headerless_tsv_taxonomy_format_validate_positive(self):
        filenames = ['headerless.tsv', '2-column.tsv', '3-column.tsv',
                     'valid-but-messy.tsv', 'many-rows.tsv']
        filepaths = [self.get_data_path(os.path.join('taxonomy', filename))
                     for filename in filenames]

        for filepath in filepaths:
            format = HeaderlessTSVTaxonomyFormat(filepath, mode='r')

            format.validate()

    def test_headerless_tsv_taxonomy_format_validate_negative(self):
        filenames = ['empty', 'blanks-and-comments', '1-column.tsv']
        filepaths = [self.get_data_path(os.path.join('taxonomy', filename))
                     for filename in filenames]

        for filepath in filepaths:
            format = HeaderlessTSVTaxonomyFormat(filepath, mode='r')

            with self.assertRaisesRegex(ValidationError,
                                        'HeaderlessTSVTaxonomy'):
                format.validate()

    def test_headerless_tsv_taxonomy_directory_format(self):
        # Basic test to verify that single-file directory format is working.
        filepath = self.get_data_path(os.path.join('taxonomy',
                                                   'headerless.tsv'))
        shutil.copy(filepath,
                    os.path.join(self.temp_dir.name, 'taxonomy.tsv'))

        format = HeaderlessTSVTaxonomyDirectoryFormat(self.temp_dir.name,
                                                      mode='r')

        format.validate()

    def test_tsv_taxonomy_format_validate_positive(self):
        filenames = ['2-column.tsv', '3-column.tsv', 'valid-but-messy.tsv',
                     'many-rows.tsv']
        filepaths = [self.get_data_path(os.path.join('taxonomy', filename))
                     for filename in filenames]

        for filepath in filepaths:
            format = TSVTaxonomyFormat(filepath, mode='r')

            format.validate()

    def test_tsv_taxonomy_format_validate_negative(self):
        filenames = ['empty', 'blanks-and-comments', '1-column.tsv',
                     'headerless.tsv', 'header-only.tsv', 'jagged.tsv']
        filepaths = [self.get_data_path(os.path.join('taxonomy', filename))
                     for filename in filenames]

        for filepath in filepaths:
            format = TSVTaxonomyFormat(filepath, mode='r')

            with self.assertRaisesRegex(ValidationError, 'TSVTaxonomy'):
                format.validate()

    def test_tsv_taxonomy_directory_format(self):
        # Basic test to verify that single-file directory format is working.
        filepath = self.get_data_path(os.path.join('taxonomy', '2-column.tsv'))
        shutil.copy(filepath,
                    os.path.join(self.temp_dir.name, 'taxonomy.tsv'))

        format = TSVTaxonomyDirectoryFormat(self.temp_dir.name, mode='r')

        format.validate()


class TestDNAFASTAFormats(TestPluginBase):
    package = 'q2_types.feature_data.tests'

    def test_dna_fasta_format_validate_positive(self):
        filepath = self.get_data_path('dna-sequences.fasta')
        format = DNAFASTAFormat(filepath, mode='r')

        format.validate()

    def test_dna_fasta_format_validate_negative(self):
        filepath = self.get_data_path('not-dna-sequences')
        format = DNAFASTAFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, 'DNAFASTA'):
            format.validate()

    def test_dna_fasta_format_empty_file(self):
        filepath = os.path.join(self.temp_dir.name, 'empty')
        with open(filepath, 'w') as fh:
            fh.write('\n')
        format = DNAFASTAFormat(filepath, mode='r')

        format.validate()

    def test_dna_fasta_format_consecutive_IDs(self):
        filepath = self.get_data_path('dna-sequences-consecutive-ids.fasta')
        format = DNAFASTAFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, 'consecutive IDs.*1'):
            format.validate()

    def test_dna_fasta_format_missing_initial_ID(self):
        filepath = self.get_data_path('dna-sequences-first-line-not-id.fasta')
        format = DNAFASTAFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, 'First line'):
            format.validate()

    def test_dna_fasta_format_corrupt_characters(self):
        filepath = self.get_data_path('dna-sequences-corrupt-characters.fasta')
        format = DNAFASTAFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, 'utf-8.*2'):
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

        with self.assertRaisesRegex(ValidationError, 'AlignedDNAFASTA'):
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
