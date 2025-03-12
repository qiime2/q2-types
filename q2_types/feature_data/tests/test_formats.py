# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
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
    AlignedDNASequencesDirectoryFormat, DifferentialDirectoryFormat,
    ProteinFASTAFormat, AlignedProteinFASTAFormat, FASTAFormat,
    MixedCaseProteinFASTAFormat,
    MixedCaseAlignedProteinFASTAFormat,
    MixedCaseAlignedProteinSequencesDirectoryFormat,
    MixedCaseProteinSequencesDirectoryFormat,
    AlignedProteinSequencesDirectoryFormat, ProteinSequencesDirectoryFormat,
    RNAFASTAFormat, RNASequencesDirectoryFormat, AlignedRNAFASTAFormat,
    AlignedRNASequencesDirectoryFormat, BLAST6DirectoryFormat,
    MixedCaseDNAFASTAFormat, MixedCaseDNASequencesDirectoryFormat,
    MixedCaseRNAFASTAFormat, MixedCaseRNASequencesDirectoryFormat,
    MixedCaseAlignedDNAFASTAFormat,
    MixedCaseAlignedDNASequencesDirectoryFormat,
    MixedCaseAlignedRNAFASTAFormat,
    MixedCaseAlignedRNASequencesDirectoryFormat,
    SequenceCharacteristicsDirectoryFormat, SequenceCharacteristicsFormat
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
        filenames = ['empty', 'blanks', '1-column.tsv']
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
        filenames = ['empty', 'blanks', '1-column.tsv']
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
        filenames = ['empty', 'blanks', '1-column.tsv',
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

    def test_tsv_taxonomy_format_column_header_lengths(self):
        filenames = ['greater-column-length.tsv', 'greater-header-length.tsv']

        filepaths = [self.get_data_path(os.path.join('taxonomy', filename))
                     for filename in filenames]

        for filepath in filepaths:
            format = TSVTaxonomyFormat(filepath, mode='r')

            with self.assertRaisesRegex(ValidationError,
                                        'line 2.*3 values.*expected 2'):
                format.validate()


class TestNucleicAcidFASTAFormats(TestPluginBase):
    package = 'q2_types.feature_data.tests'

    # DNA Format Tests
    def test_permissive_fasta_format(self):
        filepath = self.get_data_path('dna-sequences-gisaid.fasta')
        format = FASTAFormat(filepath, mode='r')

        format.validate()

    def test_dna_fasta_format_validate_positive(self):
        filepath = self.get_data_path('dna-sequences.fasta')
        format = DNAFASTAFormat(filepath, mode='r')

        format.validate()

    def test_dna_fasta_format_bom_passes(self):
        filepath = self.get_data_path('dna-with-bom-passes.fasta')
        format = DNAFASTAFormat(filepath, mode='r')

        format.validate()

    def test_dna_fasta_format_empty_file(self):
        filepath = os.path.join(self.temp_dir.name, 'empty')
        with open(filepath, 'w') as fh:
            fh.write('\n')
        format = DNAFASTAFormat(filepath, mode='r')

        format.validate()

    def test_dna_fasta_format_invalid_characters(self):
        filepath = self.get_data_path('not-dna-sequences.fasta')
        format = DNAFASTAFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, "Invalid character '1' "
                                                     ".*0 on line 2"):
            format.validate()

    def test_dna_fasta_format_validate_negative(self):
        filepath = self.get_data_path('not-dna-sequences')
        format = DNAFASTAFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, 'DNAFASTA'):
            format.validate()

    def test_dna_fasta_format_consecutive_IDs(self):
        filepath = self.get_data_path('dna-sequences-consecutive-ids.fasta')
        format = DNAFASTAFormat(filepath, mode='r')

        with self.assertRaisesRegex(
                ValidationError, 'consecutive descriptions.*1'):
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

    def test_dna_fasta_format_bom_fails(self):
        filepath = self.get_data_path('dna-with-bom-fails.fasta')
        format = DNAFASTAFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, 'First line'):
            format.validate()

    def test_dna_sequences_directory_format(self):
        filepath = self.get_data_path('dna-sequences.fasta')
        shutil.copy(filepath,
                    os.path.join(self.temp_dir.name, 'dna-sequences.fasta'))
        format = DNASequencesDirectoryFormat(self.temp_dir.name, mode='r')

        format.validate()

    def test_dna_fasta_format_duplicate_ids(self):
        filepath = self.get_data_path('dna-sequences-duplicate-id.fasta')
        format = DNAFASTAFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, '3.*duplicate.*1'):
            format.validate()

    def test_dna_fasta_format_no_id(self):
        filepath = self.get_data_path('dna-sequences-no-id.fasta')
        format = DNAFASTAFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, '1.*missing an ID'):
            format.validate()

    def test_dna_fasta_format_id_starts_with_space(self):
        filepath = self.get_data_path(
            'dna-sequences-id-starts-with-space.fasta')
        format = DNAFASTAFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, '1 starts with a space'):
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

    def test_aligned_dna_fasta_format_unaligned(self):
        filepath = self.get_data_path('dna-sequences.fasta')
        format = AlignedDNAFASTAFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError,
                                    'line 4.*length 88.*length 64'):
            format.validate()

    def test_aligned_dna_sequences_directory_format(self):
        filepath = self.get_data_path('aligned-dna-sequences.fasta')
        temp_dir = self.temp_dir.name
        shutil.copy(filepath,
                    os.path.join(temp_dir, 'aligned-dna-sequences.fasta'))
        format = AlignedDNASequencesDirectoryFormat(temp_dir, mode='r')

        format.validate()

    # RNA Format Tests
    def test_rna_fasta_format_validate_positive(self):
        filepath = self.get_data_path('rna-sequences.fasta')
        format = RNAFASTAFormat(filepath, mode='r')

        format.validate()

    def test_rna_fasta_format_bom_passes(self):
        filepath = self.get_data_path('rna-with-bom-passes.fasta')
        format = RNAFASTAFormat(filepath, mode='r')

        format.validate()

    def test_rna_fasta_format_empty_file(self):
        filepath = os.path.join(self.temp_dir.name, 'empty')
        with open(filepath, 'w') as fh:
            fh.write('\n')
        format = RNAFASTAFormat(filepath, mode='r')

        format.validate()

    def test_rna_fasta_format_invalid_characters(self):
        filepath = self.get_data_path('not-rna-sequences.fasta')
        format = RNAFASTAFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, "Invalid character '1' "
                                                     ".*0 on line 2"):
            format.validate()

    def test_rna_fasta_format_validate_negative(self):
        filepath = self.get_data_path('not-rna-sequences')
        format = RNAFASTAFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, 'RNAFASTA'):
            format.validate()

    def test_rna_fasta_format_consecutive_IDs(self):
        filepath = self.get_data_path('dna-sequences-consecutive-ids.fasta')
        format = RNAFASTAFormat(filepath, mode='r')

        with self.assertRaisesRegex(
                ValidationError, 'consecutive descriptions.*1'):
            format.validate()

    def test_rna_fasta_format_missing_initial_ID(self):
        filepath = self.get_data_path('dna-sequences-first-line-not-id.fasta')
        format = RNAFASTAFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, 'First line'):
            format.validate()

    def test_rna_fasta_format_corrupt_characters(self):
        filepath = self.get_data_path('dna-sequences-corrupt-characters.fasta')
        format = RNAFASTAFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, 'utf-8.*2'):
            format.validate()

    def test_rna_fasta_format_bom_fails(self):
        filepath = self.get_data_path('dna-with-bom-fails.fasta')
        format = RNAFASTAFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, 'First line'):
            format.validate()

    def test_rna_sequences_directory_format(self):
        filepath = self.get_data_path('rna-sequences.fasta')
        shutil.copy(filepath,
                    os.path.join(self.temp_dir.name, 'rna-sequences.fasta'))
        format = RNASequencesDirectoryFormat(self.temp_dir.name, mode='r')

        format.validate()

    def test_rna_fasta_format_duplicate_ids(self):
        filepath = self.get_data_path('rna-sequences-with-duplicate-ids.fasta')
        format = RNAFASTAFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, '6.*duplicate.*1'):
            format.validate()

    def test_rna_fasta_format_no_id(self):
        filepath = self.get_data_path('dna-sequences-no-id.fasta')
        format = RNAFASTAFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, '1.*missing an ID'):
            format.validate()

    def test_rna_fasta_format_id_starts_with_space(self):
        filepath = self.get_data_path(
            'dna-sequences-id-starts-with-space.fasta')
        format = RNAFASTAFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, '1 starts with a space'):
            format.validate()

    def test_aligned_rna_fasta_format_validate_positive(self):
        filepath = self.get_data_path('aligned-rna-sequences.fasta')
        format = AlignedRNAFASTAFormat(filepath, mode='r')

        format.validate()

    def test_aligned_rna_fasta_format_validate_negative(self):
        filepath = self.get_data_path('not-rna-sequences')
        format = AlignedRNAFASTAFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, 'AlignedRNAFASTA'):
            format.validate()

    def test_aligned_rna_fasta_format_unaligned(self):
        filepath = self.get_data_path('rna-sequences.fasta')
        format = AlignedRNAFASTAFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError,
                                    'line 4.*length 88.*length 64'):
            format.validate()

    def test_aligned_rna_sequences_directory_format(self):
        filepath = self.get_data_path('aligned-rna-sequences.fasta')
        temp_dir = self.temp_dir.name
        shutil.copy(filepath,
                    os.path.join(temp_dir, 'aligned-rna-sequences.fasta'))
        format = AlignedRNASequencesDirectoryFormat(temp_dir, mode='r')

        format.validate()

    # Mixed Case DNA
    def test_mixed_case_dna_fasta_format_validate_positive(self):
        filepath = self.get_data_path('dna-sequences-mixed-case.fasta')
        format = MixedCaseDNAFASTAFormat(filepath, mode='r')

        format.validate()

    def test_mixed_case_dna_format_bom_passes(self):
        filepath = self.get_data_path('dna-mixed-case-with-bom-passes.fasta')
        format = MixedCaseDNAFASTAFormat(filepath, mode='r')

        format.validate()

    def test_mixed_case_dna_fasta_format_bom_fails(self):
        filepath = self.get_data_path('dna-with-bom-fails.fasta')
        format = MixedCaseDNAFASTAFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, 'First line'):
            format.validate()

    def test_mixed_case_dna_fasta_format_empty_file(self):
        filepath = os.path.join(self.temp_dir.name, 'empty')
        with open(filepath, 'w') as fh:
            fh.write('\n')
        format = MixedCaseDNAFASTAFormat(filepath, mode='r')

        format.validate()

    def test_mixed_case_dna_fasta_format_invalid_characters(self):
        filepath = self.get_data_path('not-dna-sequences.fasta')
        format = MixedCaseDNAFASTAFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, "Invalid character '1' "
                                    ".*0 on line 2"):
            format.validate()

    def test_mixed_case_dna_format_validate_negative(self):
        filepath = self.get_data_path('not-dna-sequences')
        format = MixedCaseDNAFASTAFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, 'DNAFASTA'):
            format.validate()

    def test_mixed_case_dna_fasta_format_consecutive_IDs(self):
        filepath = self.get_data_path('dna-sequences-consecutive-ids.fasta')
        format = MixedCaseDNAFASTAFormat(filepath, mode='r')

        with self.assertRaisesRegex(
                ValidationError, 'consecutive descriptions.*1'):
            format.validate()

    def test_mixed_case_dna_fasta_format_missing_initial_ID(self):
        filepath = self.get_data_path('dna-sequences-first-line-not-id.fasta')
        format = MixedCaseDNAFASTAFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, 'First line'):
            format.validate()

    def test_mixed_case_dna_fasta_format_corrupt_characters(self):
        filepath = self.get_data_path('dna-sequences-corrupt-characters.fasta')
        format = MixedCaseDNAFASTAFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, 'utf-8.*2'):
            format.validate()

    def test_mixed_case_dna_sequences_directory_format(self):
        filepath = self.get_data_path('dna-sequences-mixed-case.fasta')
        shutil.copy(filepath,
                    os.path.join(self.temp_dir.name,
                                 'dna-sequences.fasta'))
        format = MixedCaseDNASequencesDirectoryFormat(self.temp_dir.name,
                                                      mode='r')

        format.validate()

    def test_mixed_case_dna_fasta_format_duplicate_ids(self):
        filepath = self.get_data_path(
                          'dna-sequences-mixed-case-with-duplicate-ids.fasta')
        format = MixedCaseDNAFASTAFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, '6.*duplicate.*1'):
            format.validate()

    def test_mixed_case_dna_fasta_format_no_id(self):
        filepath = self.get_data_path('dna-sequences-no-id.fasta')
        format = MixedCaseDNAFASTAFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, '1.*missing an ID'):
            format.validate()

    def test_mixed_case_dna_fasta_format_id_starts_with_space(self):
        filepath = self.get_data_path(
            'dna-sequences-id-starts-with-space.fasta')
        format = MixedCaseDNAFASTAFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, '1 starts with a space'):
            format.validate()

    # Mixed Case Aligned DNA

    def test_mixed_case_aligned_dna_fasta_format_validate_positive(self):
        filepath = self.get_data_path('aligned-dna-sequences-mixed-case.fasta')
        format = MixedCaseAlignedDNAFASTAFormat(filepath, mode='r')

        format.validate()

    def test_mixed_case_aligned_dna_fasta_format_validate_negative(self):
        filepath = self.get_data_path('not-dna-sequences')
        format = MixedCaseAlignedDNAFASTAFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError,
                                    'MixedCaseAlignedDNAFASTA'):
            format.validate()

    def test_mixed_case_aligned_dna_fasta_format_unaligned(self):
        filepath = self.get_data_path('dna-sequences-mixed-case.fasta')
        format = MixedCaseAlignedDNAFASTAFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError,
                                    'line 4.*length 88.*length 64'):
            format.validate()

    def test_mixed_case_aligned_dna_sequences_directory_format(self):
        filepath = self.get_data_path('aligned-dna-sequences-mixed-case.fasta')
        temp_dir = self.temp_dir.name
        shutil.copy(filepath,
                    os.path.join(temp_dir,
                                 'aligned-dna-sequences.fasta'))
        format = MixedCaseAlignedDNASequencesDirectoryFormat(
                                          temp_dir, mode='r')

        format.validate()

    # Mixed Case Aligned RNA

    def test_mixed_case_aligned_rna_fasta_format_validate_positive(self):
        filepath = self.get_data_path('aligned-rna-sequences-mixed-case.fasta')
        format = MixedCaseAlignedRNAFASTAFormat(filepath, mode='r')

        format.validate()

    def test_mixed_case_aligned_rna_fasta_format_validate_negative(self):
        filepath = self.get_data_path('not-dna-sequences')
        format = MixedCaseAlignedRNAFASTAFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError,
                                    'MixedCaseAlignedRNAFASTA'):
            format.validate()

    def test_mixed_case_aligned_rna_fasta_format_unaligned(self):
        filepath = self.get_data_path('rna-sequences-mixed-case.fasta')
        format = MixedCaseAlignedRNAFASTAFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError,
                                    'line 4.*length 88.*length 64'):
            format.validate()

    def test_mixed_case_aligned_rna_sequences_directory_format(self):
        filepath = self.get_data_path('aligned-rna-sequences-mixed-case.fasta')
        temp_dir = self.temp_dir.name
        shutil.copy(filepath,
                    os.path.join(temp_dir,
                                 'aligned-rna-sequences.fasta'))
        format = MixedCaseAlignedRNASequencesDirectoryFormat(
                                          temp_dir, mode='r')

        format.validate()

    # Mixed Case RNA
    def test_mixed_case_rna_fasta_format_validate_positive(self):
        filepath = self.get_data_path('rna-sequences-mixed-case.fasta')
        format = MixedCaseRNAFASTAFormat(filepath, mode='r')

        format.validate()

    def test_mixed_case_rna_format_bom_passes(self):
        filepath = self.get_data_path('rna-mixed-case-with-bom-passes.fasta')
        format = MixedCaseRNAFASTAFormat(filepath, mode='r')

        format.validate()

    def test_mixed_case_rna_fasta_format_bom_fails(self):
        filepath = self.get_data_path('dna-with-bom-fails.fasta')
        format = MixedCaseRNAFASTAFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, 'First line'):
            format.validate()

    def test_mixed_case_rna_fasta_format_empty_file(self):
        filepath = os.path.join(self.temp_dir.name, 'empty')
        with open(filepath, 'w') as fh:
            fh.write('\n')
        format = MixedCaseRNAFASTAFormat(filepath, mode='r')

        format.validate()

    def test_mixed_case_rna_fasta_format_invalid_characters(self):
        filepath = self.get_data_path('not-rna-sequences.fasta')
        format = MixedCaseRNAFASTAFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, "Invalid character '1' "
                                    ".*0 on line 2"):
            format.validate()

    def test_mixed_case_rna_format_validate_negative(self):
        filepath = self.get_data_path('not-rna-sequences')
        format = MixedCaseRNAFASTAFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, 'RNAFASTA'):
            format.validate()

    def test_mixed_case_rna_fasta_format_consecutive_IDs(self):
        filepath = self.get_data_path('dna-sequences-consecutive-ids.fasta')
        format = MixedCaseRNAFASTAFormat(filepath, mode='r')

        with self.assertRaisesRegex(
                ValidationError, 'consecutive descriptions.*1'):
            format.validate()

    def test_mixed_case_rna_fasta_format_missing_initial_ID(self):
        filepath = self.get_data_path('dna-sequences-first-line-not-id.fasta')
        format = MixedCaseRNAFASTAFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, 'First line'):
            format.validate()

    def test_mixed_case_rna_fasta_format_corrupt_characters(self):
        filepath = self.get_data_path('dna-sequences-corrupt-characters.fasta')
        format = MixedCaseRNAFASTAFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, 'utf-8.*2'):
            format.validate()

    def test_mixed_case_rna_sequences_directory_format(self):
        filepath = self.get_data_path('rna-sequences-mixed-case.fasta')
        shutil.copy(filepath,
                    os.path.join(self.temp_dir.name,
                                 'rna-sequences.fasta'))
        format = MixedCaseRNASequencesDirectoryFormat(self.temp_dir.name,
                                                      mode='r')

        format.validate()

    def test_mixed_case_rna_fasta_format_duplicate_ids(self):
        filepath = self.get_data_path(
                          'rna-sequences-mixed-case-with-duplicate-ids.fasta')
        format = MixedCaseRNAFASTAFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, '6.*duplicate.*1'):
            format.validate()

    def test_mixed_case_rna_fasta_format_no_id(self):
        filepath = self.get_data_path('dna-sequences-no-id.fasta')
        format = MixedCaseRNAFASTAFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, '1.*missing an ID'):
            format.validate()

    def test_mixed_case_rna_fasta_format_id_starts_with_space(self):
        filepath = self.get_data_path(
            'dna-sequences-id-starts-with-space.fasta')
        format = MixedCaseRNAFASTAFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, '1 starts with a space'):
            format.validate()


class TestDifferentialFormat(TestPluginBase):
    package = 'q2_types.feature_data.tests'

    def test_differential_format(self):
        filepath = self.get_data_path('differentials.tsv')
        temp_dir = self.temp_dir.name
        shutil.copy(filepath,
                    os.path.join(temp_dir, 'differentials.tsv'))
        format = DifferentialDirectoryFormat(temp_dir, mode='r')
        format.validate()
        self.assertTrue(True)

    def test_differential_format_empty(self):
        filepath = self.get_data_path('empty_differential.tsv')
        temp_dir = self.temp_dir.name
        shutil.copy(filepath,
                    os.path.join(temp_dir, 'differentials.tsv'))

        with self.assertRaisesRegex(ValidationError, 'least 1 column'):
            format = DifferentialDirectoryFormat(temp_dir, mode='r')
            format.validate()

    def test_differential_format_not(self):
        filepath = self.get_data_path('not_differential.tsv')
        temp_dir = self.temp_dir.name
        shutil.copy(filepath,
                    os.path.join(temp_dir, 'differentials.tsv'))

        with self.assertRaises(ValidationError):
            format = DifferentialDirectoryFormat(temp_dir, mode='r')
            format.validate()

    def test_differential_format_inf(self):
        filepath = self.get_data_path('inf_differential.tsv')
        temp_dir = self.temp_dir.name
        shutil.copy(filepath,
                    os.path.join(temp_dir, 'differentials.tsv'))

        with self.assertRaisesRegex(ValidationError, 'numeric'):
            format = DifferentialDirectoryFormat(temp_dir, mode='r')
            format.validate()

    def test_differential_format_bad_type(self):
        filepath = self.get_data_path('bad_differential.tsv')
        temp_dir = self.temp_dir.name
        shutil.copy(filepath,
                    os.path.join(temp_dir, 'differentials.tsv'))

        with self.assertRaisesRegex(ValidationError, 'numeric'):
            format = DifferentialDirectoryFormat(temp_dir, mode='r')
            format.validate()


class TestProteinFASTAFormats(TestPluginBase):
    package = 'q2_types.feature_data.tests'

    def test_protein_fasta_format_validate_positive(self):
        filepath = self.get_data_path('protein-sequences.fasta')
        format = ProteinFASTAFormat(filepath, mode='r')

        format.validate()
        format.validate('min')

    def test_protein_fasta_format_invalid_characters(self):
        filepath = self.get_data_path('not-dna-sequences.fasta')
        format = ProteinFASTAFormat(filepath, mode='r')

        with self.assertRaisesRegex(
                ValidationError, "Invalid character '1' .*0 on line 2"):
            format.validate()

    def test_protein_fasta_format_empty_file(self):
        filepath = os.path.join(self.temp_dir.name, 'empty')
        with open(filepath, 'w') as fh:
            fh.write('\n')
        format = ProteinFASTAFormat(filepath, mode='r')

        format.validate()

    def test_protein_sequences_directory_format(self):
        filepath = self.get_data_path('protein-sequences.fasta')
        shutil.copy(filepath,
                    os.path.join(
                        self.temp_dir.name, 'protein-sequences.fasta'))
        format = ProteinSequencesDirectoryFormat(self.temp_dir.name, mode='r')

        format.validate()

    def test_aligned_protein_fasta_format_validate_positive(self):
        filepath = self.get_data_path('aligned-protein-sequences.fasta')
        format = AlignedProteinFASTAFormat(filepath, mode='r')

        format.validate()
        format.validate('min')

    def test_aligned_protein_fasta_format_unaligned(self):
        filepath = self.get_data_path('protein-sequences.fasta')
        format = AlignedProteinFASTAFormat(filepath, mode='r')

        with self.assertRaisesRegex(
                ValidationError, 'line 5 was length 94.* previous .* 70'):
            format.validate()

    def test_aligned_protein_sequences_directory_format(self):
        filepath = self.get_data_path('aligned-protein-sequences.fasta')
        temp_dir = self.temp_dir.name
        shutil.copy(filepath,
                    os.path.join(temp_dir, 'aligned-protein-sequences.fasta'))
        format = AlignedProteinSequencesDirectoryFormat(temp_dir, mode='r')

        format.validate()

    def test_mixed_case_aligned_protein_fasta_format_validate_positive(self):
        filepath = self.get_data_path(
            'mixed-case-aligned-protein-sequences.fasta'
            )
        format = MixedCaseAlignedProteinFASTAFormat(filepath, mode='r')

        format.validate()
        format.validate('min')

    def test_mixed_case_aligned_protein_fasta_format_unaligned(self):
        filepath = self.get_data_path('mixed-case-protein-sequences.fasta')
        format = MixedCaseAlignedProteinFASTAFormat(filepath, mode='r')

        with self.assertRaisesRegex(
                ValidationError, 'line 5 was length 95.* previous .* 70'):
            format.validate()

    def test_mixed_case_protein_fasta_format_validate_positive(self):
        filepath = self.get_data_path('mixed-case-protein-sequences.fasta')
        format = MixedCaseProteinFASTAFormat(filepath, mode='r')

        format.validate()

    def test_mixed_case_protein_fasta_format_invalid_characters(self):
        filepath = self.get_data_path(
            'mixed-case-aligned-protein-sequences.fasta'
            )
        format = MixedCaseProteinFASTAFormat(filepath, mode='r')

        with self.assertRaisesRegex(
                ValidationError,
                "Invalid character '-' at position 0 on line 2"):
            format.validate()

    def test_mixed_case_aligned_protein_sequences_directory_format(self):
        filepath = self.get_data_path(
            'mixed-case-aligned-protein-sequences.fasta'
            )
        temp_dir = self.temp_dir.name
        shutil.copy(filepath,
                    os.path.join(
                        temp_dir,
                        'aligned-protein-sequences.fasta'
                        )
                    )
        format = MixedCaseAlignedProteinSequencesDirectoryFormat(
            temp_dir, mode='r'
            )

        format.validate()

    def test_mixed_case_protein_sequences_directory_format(self):
        filepath = self.get_data_path('mixed-case-protein-sequences.fasta')
        temp_dir = self.temp_dir.name
        shutil.copy(filepath,
                    os.path.join(
                        temp_dir, 'protein-sequences.fasta'
                        )
                    )
        format = MixedCaseProteinSequencesDirectoryFormat(temp_dir, mode='r')

        format.validate()


class TestBLAST6Format(TestPluginBase):
    package = 'q2_types.feature_data.tests'

    def test_blast6_format(self):
        filepath = self.get_data_path('blast6.tsv')
        temp_dir = self.temp_dir.name
        shutil.copy(filepath, os.path.join(temp_dir, 'blast6.tsv'))
        format = BLAST6DirectoryFormat(temp_dir, mode='r')
        format.validate()
        self.assertTrue(True)

    def test_blast6_format_empty(self):
        temp_dir = self.temp_dir.name
        open(os.path.join(temp_dir, 'blast6.tsv'), 'w').close()
        with self.assertRaisesRegex(ValidationError, 'BLAST6 file is empty.'):
            BLAST6DirectoryFormat(temp_dir, mode='r').validate()

    def test_blast6_format_invalid(self):
        filepath = self.get_data_path('blast6_invalid.tsv')
        temp_dir = self.temp_dir.name
        shutil.copy(filepath, os.path.join(temp_dir, 'blast6.tsv'))
        with self.assertRaisesRegex(ValidationError, 'Invalid BLAST6 format.'):
            BLAST6DirectoryFormat(temp_dir, mode='r').validate()


class TestSequenceCharacteristicsFormat(TestPluginBase):
    package = 'q2_types.feature_data.tests'

    def test_sequence_characteristics_directory_format(self):
        filepath = self.get_data_path('sequence_characteristics_length.tsv')
        temp_dir = self.temp_dir.name
        shutil.copy(filepath, os.path.join(temp_dir,
                                           'sequence_characteristics.tsv'))
        format = SequenceCharacteristicsDirectoryFormat(temp_dir, mode='r')
        format.validate()

    def test_sequence_characteristics_format(self):
        filepath = self.get_data_path('sequence_characteristics_length.tsv')
        format = SequenceCharacteristicsFormat(filepath, mode='r')
        format.validate()

    def test_sequence_characteristics_format_empty(self):
        path = self.get_data_path('empty.tsv')
        format = SequenceCharacteristicsFormat(path, mode='r')
        with self.assertRaises(ValidationError) as context:
            format.validate()
        self.assertEqual(str(context.exception), 'File cannot be empty.')

    def test_sequence_characteristics_format_only_index(self):
        path = self.get_data_path('sequence_characteristics_only_index.tsv')
        format = SequenceCharacteristicsFormat(path, mode='r')
        with self.assertRaises(ValidationError) as context:
            format.validate()
        self.assertEqual(str(context.exception),
                         'File needs to have at least two columns.')


if __name__ == '__main__':
    unittest.main()
